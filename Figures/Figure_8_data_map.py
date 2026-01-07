# %% 
from sqlalchemy import create_engine, text

import geopandas as gpd

import matplotlib.pyplot as plt
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.gridspec as gridspec

from shapely.geometry import Point
from shapely.geometry import box

import numpy as np
from rasterio.features import rasterize
from affine import Affine

db = 'ResRoute'
db_connection_url = "postgresql://postgres:postgres@localhost:5432/"+db
con = create_engine(db_connection_url)
area  = 'all'


# %%


plt.rcParams.update({'font.size': 20})

hl = '#D8B7DD'
hm = '#800080'
hd = '#4B0082'
al = '#FFD700'
am = '#FFA500'
ad = '#FF8C00'

#%%

# Create the grid for subplots (4 subplots, one for each season) with space for the colorbar
querry_hum = """
select ST_MakeLine(points.geom order by points.temps) as geom
from indiv_Human
inner join trajectories
	on trajectories.id_indiv = indiv_Human.id_indiv
inner join sub_trajectories
	on sub_trajectories.id_traj = trajectories.id_traj
inner join public.points
	on points.id_sub_traj = sub_trajectories.id_sub_traj
group by trajectories.id_traj
"""
    
traj_human = gpd.GeoDataFrame.from_postgis(querry_hum, con)

querry_cham = """
select st_collect(geom) as geom
from points
where outlier is not true
and species = 'chamois'
group by id_indiv, date(temps)
"""

querry_cham = """
SELECT ST_Collect(points.geom) AS geom
FROM recorded_animal
INNER JOIN trajectories
    ON trajectories.id_indiv = recorded_animal.id_indiv
INNER JOIN sub_trajectories
    ON sub_trajectories.id_traj = trajectories.id_traj
INNER JOIN public.points
    ON points.id_sub_traj = sub_trajectories.id_sub_traj
WHERE points.geom IS NOT NULL
and points.outlier is not null
GROUP BY trajectories.id_traj;
"""


traj_chamois = gpd.GeoDataFrame.from_postgis(querry_cham, con)

#%% 

fig, ax = plt.subplots(figsize=(10, 10))

if area == 'all':
    ymin = 6500012.5000600000000 + 25 * 176
    ymax = ymin + 25 * 640
    xmin = 924987.500000000000 + 25 * 870
    xmax = xmin + 25 * 400 #320
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
traj_human = traj_human[~traj_human.geometry.is_empty & traj_human.geometry.is_valid].copy()
bbox = box(*bounds)
ppa_clipped = traj_human[traj_human.geometry.intersects(bbox)].copy()
shapes = [(geom, 1) for geom in traj_human.geometry]
raster = np.zeros((height, width), dtype=np.uint8)


for shape in shapes:
    rasterized = rasterize(
        [shape],
        out_shape=(height, width),
        transform=transform,
        dtype=np.uint8  # <-- Ensures compatible dtype
    )
    raster += rasterized


#for shape in shapes:
#    raster += rasterize([shape], out_shape=(height, width), transform=transform)

    # Plot the raster with colormap
masked_human  = np.ma.masked_where(raster == 0, raster)

cmap=plt.cm.winter_r
img_human = ax.imshow(masked_human , cmap=cmap, extent=bounds, origin='upper', zorder=5)  # Set colorbar range


gs = gridspec.GridSpec(1, 2, width_ratios=[0.1, 0.9], wspace=0.05)

traj_chamois = traj_chamois[~traj_chamois.geometry.is_empty & traj_chamois.geometry.is_valid].copy()
bbox = box(*bounds)
ppa_clipped = traj_chamois[traj_chamois.geometry.intersects(bbox)].copy()
shapes = [(geom, 1) for geom in traj_chamois.geometry]
raster = np.zeros((height, width), dtype=np.uint8)

for shape in shapes:
    rasterized = rasterize(
        [shape],
        out_shape=(height, width),
        transform=transform,
        dtype=np.uint8  # <-- Ensures compatible dtype
    )
    raster += rasterized

#for shape in shapes:
#    raster += rasterize([shape], out_shape=(height, width), transform=transform)

    # Plot the raster with colormap
masked_chamois  = np.ma.masked_where(raster == 0, raster)

cmap= plt.cm.autumn_r
img_chamois = ax.imshow(masked_chamois , cmap=cmap, extent=bounds, origin='upper', zorder=3) 

# Add colorbar for human raster
# Create two separate axes for colorbars to the left of the map
cb_ax_human = fig.add_axes([0.15, 0.60, 0.015, 0.33])   # [left, bottom, width, height]
cb_ax_chamois = fig.add_axes([0.15, 0.25, 0.015, 0.33])

# Add colorbars
cbar_human   = fig.colorbar(img_human  , cax=cb_ax_human,   orientation='vertical')
cbar_chamois = fig.colorbar(img_chamois, cax=cb_ax_chamois, orientation='vertical')

# Label settings
for cbar, label in zip([cbar_human, cbar_chamois], ['Human Trajectories', 'Chamois Trajectories']):
    cbar.set_label(label, fontsize=10, labelpad=10)
    cbar.ax.yaxis.set_label_position('left')
    cbar.ax.yaxis.tick_left()


ax_inset = fig.add_axes([0.05, 0.05, 0.14, 0.14])  # Coordinates for the inset


con = create_engine(db_connection_url)

france = """
    select * from france
    """

france  = gpd.GeoDataFrame.from_postgis(france, con)

# Plot the GeoDataFrame
france.plot(ax=ax_inset, edgecolor='black', facecolor='lightblue') 

france = france.to_crs(2154)
france.plot(ax=ax_inset, color='lightblue', edgecolor='black', alpha = 0.5)

legend_elements = [ Line2D([0], [0], marker='*', color='w', label='Trapping Sites',
                                         markerfacecolor='purple', markersize=20),
                    Line2D([0], [0], color='black', lw=4, label='Roads'),
                    Patch(facecolor='grey', edgecolor='grey',alpha=0.75, label='Wildlife Reserve'),

                    ]


ax.legend(handles=legend_elements, loc='upper right')

# Set the limits to show the whole of France
ax_inset.set_xlim((95092.04771388115, 1119290.9349461338))
ax_inset.set_ylim((6089957.630902461, 7166041.897185192))

# Add a simple patch to highlight the region of interest
rect = plt.Rectangle((946371.0, 6504490.0), 955867.0 - 946371.0, 6517892.0 - 6504490.0, linewidth=2, edgecolor='red', facecolor='none')
ax_inset.add_patch(rect)

# Optionally, you can plot a map of France using a shapefile
# ax_inset = gpd.read_file('path_to_france_shapefile.shp')
# ax_inset.plot(ax=ax_inset)

# Remove the axis labels and ticks for the inset map
ax_inset.set_xticks([])
ax_inset.set_yticks([])


# Move labels to the left side of each colorbar

ax.tick_params(left=False, right=False, labelleft=False, labelbottom=False, bottom=False)
ax.set_facecolor('lightgrey')
ax.set_ylim([ymin, ymax])
ax.set_xlim([xmin, xmax])
ax.set_aspect('equal')
ax.add_artist(ScaleBar(1, location="lower right"))


coords = [
    (45.6984, 6.1928),
    (45.6894, 6.1914),
    (45.6263, 6.2232),
    (45.6247, 6.2394)
]

# Create GeoDataFrame with original coordinates (WGS84 - EPSG:4326)
gdf = gpd.GeoDataFrame(
    {'geometry': [Point(lon, lat) for lat, lon in coords]},
    crs="EPSG:4326"  # WGS84 coordinate system
)

# Convert the coordinates to EPSG:2143 (local projection)
gdf = gdf.to_crs(epsg=2154)

# Plot the points in the new coordinate system (EPSG:2143)
gdf.plot(ax=ax, color='purple', edgecolor='black',marker='*', markersize=50, zorder=40)

con = create_engine(db_connection_url)

edges = """
    select * from edges
    """

edges  = gpd.GeoDataFrame.from_postgis(edges, con)

con = create_engine(db_connection_url)

bauges = """
    select * from bauges
    """

bauges = gpd.GeoDataFrame.from_postgis(bauges, con)

bauges.plot(ax=ax, facecolor='grey', alpha=1, zorder=0)
edges.plot(ax=ax, color='black', alpha=0.50, zorder=1)


#plt.tight_layout()
plt.show()

#%%
