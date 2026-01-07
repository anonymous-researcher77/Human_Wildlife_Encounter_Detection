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

with temp_ as (
select
	source,
	traj_.id_traj, 
	(count_points-count_missing_geom)/EXTRACT(EPOCH FROM (MAX(subtraj_.end_time) - MIN(subtraj_.start_time))) AS temp_gran,
	(count_points-count_missing_geom)/st_length(traj_.geom) as spac_gran,
	traj_.temporal_granularity,
	traj_.spatial_granularity
from trajectories as traj_
inner join indiv_human as ih_
	on traj_.id_indiv = ih_.id_indiv
inner join sub_trajectories as subtraj_
	on traj_.id_traj = subtraj_.id_traj
where st_length(traj_.geom) != 0
group by source, traj_.id_traj
having EXTRACT(EPOCH FROM (MAX(subtraj_.end_time) - MIN(subtraj_.start_time)))>0
	and count_points-count_missing_geom > 0 
)

select source, count(*), '1/' || round(1/avg(temp_gran)) as temp_gran,  '1/' || round(1/avg(spac_gran)) as spac_gran
from temp_
group by source

"""

table_3 = pd.read_sql_query(sql_query, con)
table_3

# %%
