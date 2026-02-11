# %% PLOT RAST of the things

import sys
import os

folder_path =        r"ADD PATH TO TRACKLIB FOLDER"
db_connection_url   = "postgresql://postgres:postgres@localhost:5432/ResRoute"
elevation_path      = 'ADD PATH TO ELEVATION FILE => /bouge_elev.tif'

main_folder_path    = os.path.dirname(os.path.dirname(__file__))

if folder_path not in sys.path:
    sys.path.insert(0, folder_path)

if main_folder_path not in sys.path:
    sys.path.insert(0, main_folder_path)

import my_utils_plotting
from affine import Affine
import matplotlib.pyplot as plt
from rasterio.features import rasterize
import numpy as np
from sqlalchemy import create_engine  , text
import geopandas as gpd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib_scalebar.scalebar import ScaleBar
from shapely.geometry import box
import rasterio
from rasterio.windows import from_bounds
import pandas as pd

area = 'all'
when = 'all'
season = 'all'
r_p = 15

spotting_table  = 'exp__encounter_event_default'
encounter_table = 'exp__encounter_default'
da_table        = 'exp__hda_default'
ppa_table       = 'exp__ppa_default'
traj_int        = 'exp__traj_ints_default'
group_by        = 'traj_human, indiv_animal'

# %%

plt.rcParams.update({'font.size': 20})

con = create_engine(db_connection_url)

edges = """
    select * from edges
    """

edges  = gpd.GeoDataFrame.from_postgis(edges, con)

bauges = """
    select * from bauges
    """

bauges = gpd.GeoDataFrame.from_postgis(bauges, con)

# %%

# Define the seasons
seasons = ['spring', 'summer', 'fall', 'winter']

# Create the grid for subplots (4 subplots, one for each season) with space for the colorbar
fig = plt.figure(figsize=(20, 13))

gs = fig.add_gridspec(2, 4, height_ratios=[1, 0.05])  # 1 row for the maps, 1 row for the colorbar

# Create axes for the maps
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[0, 3])

# Loop over seasons to generate the plots
for i, season in enumerate(seasons):
    ax = [ax1, ax2, ax3, ax4][i]  # Select the subplot for the current season
    
    # Query for ppa data for the current season
    ppa = my_utils_plotting.querry_ppa_indiv(spotting_table, 
                           encounter_table, 
                           ppa_table, 
                           time=when,
                           time_style='DD2',
                           season=season, 
                           vis=True, 
                           r_p=r_p,
                           group_by=group_by, 
                           db_connection_url=db_connection_url)

    # Set bounds for the raster
    if area == 'all':
        ymin = 6500012.5000600000000 + 25 * 176
        ymax = ymin + 25 * 640
        xmin = 924987.500000000000 + 25 * 870
        xmax = xmin + 25 * 320
    elif area == 'north':
        ymin = 6513412.50006
        ymax = 6513412.50006 + 4000
        xmin = 945737.5
        xmax = 945737.5 + 4000
    else:
        print('To do for south area')
        ymin, xmin = [], []

    bounds = [xmin, xmax, ymin, ymax]
    res = 25  # resolution in CRS units (e.g., 10 meters)
    width = int((xmax - xmin) / res)
    height = int((ymax - ymin) / res)
    
    transform = Affine(res, 0, bounds[0], 0, -res, bounds[3])

    # Rasterize: count overlaps
    ppa = ppa[~ppa.geometry.is_empty & ppa.geometry.is_valid].copy()
    mmm = np.median(ppa['geom'].area)
    bbox = box(*bounds)
    ppa_clipped = ppa[ppa.geometry.intersects(bbox)].copy()
    shapes = [(geom, 1) for geom in ppa.geometry]
    raster = np.zeros((height, width), dtype=np.uint8)


    for shape in shapes:
        rasterized = rasterize(
            [shape],
            out_shape=(height, width),
            transform=transform,
            dtype=np.uint32  # <-- Ensures this has been changed from 8 to 32 to fix th figure
        )
        raster += rasterized
    print(np.max(raster))

    #for shape in shapes:
    #    raster += rasterize([shape], out_shape=(height, width), transform=transform)

    # Plot the raster with colormap
    masked = np.ma.masked_where(raster == 0, raster)
    cmap = plt.cm.RdBu_r
    img = ax.imshow(masked, cmap=cmap, extent=bounds, origin='upper', zorder=15, vmin=1, vmax=255)  # Set colorbar range

    # Plot additional elements
    bauges.plot(ax=ax, facecolor='green', alpha=1, zorder=0)
    edges.plot(ax=ax, color='black', alpha=0.50, zorder=5)
    legend_elements = [
        Line2D([0], [0], color='black', lw=4, label='Roads', alpha=0.15),
        Patch(facecolor='green', edgecolor='black', label='Wildlife Reserve'),
    ]

    # Customize the plot
    ax.tick_params(left=False, right=False, labelleft=False, labelbottom=False, bottom=False)
    ax.set_facecolor('grey')
    ax.set_ylim([ymin, ymax])
    ax.set_xlim([xmin, xmax])
    ax.set_aspect('equal')
    ax.add_artist(ScaleBar(1, location="lower right"))

    # Set the title for each subplot
    ax.set_title(f"{season.capitalize()}")

# Create a colorbar at the bottom of the figure (using the last subplot's image for the colorbar)
cbar_ax = fig.add_subplot(gs[1, :])  # This is the bottom row that spans all columns
cbar = fig.colorbar(img, cax=cbar_ax, orientation='horizontal')
cbar.set_label('Number of overlapping $ECA^a$ from distinct human trajectory and recorded animal pairs')
cbar.set_ticks([1, 50, 100, 150, 200, 250])  # Optional: Set ticks for better readability


ax4.legend(handles=legend_elements, loc='upper right')

# Adjust layout to make everything tighter
plt.subplots_adjust(hspace=0.2, wspace=0.3)  # Adjust horizontal and vertical spacing

plt.tight_layout()
plt.show()

# %%
