# %% 

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import geopandas as gpd
from sqlalchemy import create_engine  
import os

from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

plt.rcParams.update({'font.size': 22})

# Database connection and SQL queries
db = 'ResRoute'
db_connection_url = "postgresql://postgres:postgres@localhost:5432/"+db

head = 'exp__'

# %% 
con = create_engine(db_connection_url)

hl = '#D8B7DD'
hm = '#800080'
hd = '#4B0082'
al = '#FFD700'
am = '#FFA500'
ad = '#FF8C00'
# %% 

sql1 = """
select * from edges
"""
df  = gpd.GeoDataFrame.from_postgis(sql1, con)


sql2 = """
select * from bauges
"""
df2 = gpd.GeoDataFrame.from_postgis(sql2, con)

con = create_engine(db_connection_url)


# %%

sql3 = """
select st_union(eca_a) as geom
from """+head+"""encounter_default	as a_

"""

sql4 = """
select st_union(eca_h) as geom
from """+head+"""encounter_default	as a_
"""

df7 = gpd.GeoDataFrame.from_postgis(sql3, con)
df8 = gpd.GeoDataFrame.from_postgis(sql4, con)


xmin = 950744.6176552727 - 16000/2
xmax = 950744.6176552727 + 16000/2
ymin = 6512411.741993718 - 16000/2
ymax = 6512411.741993718 + 16000/2


x_min = 942749.6327063197
y_min = 6504411.741993718
x_max = 958739.6026042257
y_max = 6520411.741993718
ymin = 6504412.5 # y_min
ymax = 6520412.5 # y_max
xmin = 946737.5
xmax = 956737.5


# %%

# Plot using Matplotlib
fig, ax = plt.subplots(figsize=(10, 10))

plt.rcParams.update({'font.size': 22})


# Add basemap (OpenStreetMap)
#ctx.add_basemap(ax, crs=encounter_df.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik, zoom=10)

df.plot(ax=ax, color='black', edgecolor='black', alpha=0.33)
df2.plot(ax=ax, color='green', edgecolor='black', alpha=0.5)

df7.plot(ax=ax, color=am, edgecolor=am, markersize = 1,  alpha=1)
df8.plot(ax=ax, color=hm, edgecolor=hm, markersize = 1,  alpha=1)


legend_elements = [Line2D([0], [0], color='black', lw=4, label='Routes', alpha=0.33),
                   Patch(facecolor='green', edgecolor='black', alpha=0.5, label='Wildlife Reserve'),
                   Patch(facecolor=hm, edgecolor=hm, label='$ECA^{Human}$'),
                   Patch(facecolor=am, edgecolor=am, label='$ECA^{Animal}$'),]

ax.legend(handles=legend_elements, loc='upper right')

ax.set_ylim([ymin, ymax])
ax.set_xlim([xmin, xmax])

ax.set_aspect('equal')
ax.get_aspect()
ax.add_artist(ScaleBar(1, location="lower right"))

plt.tick_params(left = False, right = False , labelleft = False , 
                labelbottom = False, bottom = False) 


# Show the plot
plt.tight_layout()
plt.show()


# %%
