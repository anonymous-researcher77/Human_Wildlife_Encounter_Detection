#%%

from sqlalchemy import create_engine, text
import pandas as pd

# Create an engine that connects to your database
db          =  'ResRoute'
db_user     =  'postgres'
db_password =  'postgres'
db_connection_url = "postgresql://"+db_user+":"+db_password+"@localhost:5432/"+db
con = create_engine(db_connection_url)


# %%
# SQL query combining all the queries you provided
sql_query = """

select
  count(*) as No_of_traj,
  case
    when count_points  >= 144 then '>=144 points (~10min)'
    when count_points  >= 72 and count_points - count_missing_geom < 144 then '72-143 points (~10-20min)'
    when count_points  >= 48 and count_points - count_missing_geom < 72 then '48-71 points (~20-30min)'
    when count_points  >= 24 and count_points - count_missing_geom < 48 then '24-47 points (~30-60min)'
    when count_points  >= 3 and count_points - count_missing_geom < 24 then '3-23 points (~8 hours- 1 hour)'
    when count_points  >= 1 and count_points - count_missing_geom < 3 then '1-2 points (~8 hours- 24 hour)'
 end as category,
 	'1/' || ROUND(
        AVG(
            ST_Length(tj.geom)::numeric 
            / (count_points - count_missing_geom)
        )::numeric
     , 0) as Spatial_granularity
from trajectories as tj
inner join recorded_animal as ra on tj.id_indiv = ra.id_indiv
group by category;

"""

table_2 = pd.read_sql_query(sql_query, con)
table_2

# %%
