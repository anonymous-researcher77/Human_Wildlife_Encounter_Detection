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
with hums_ as (
SELECT
	CASE
        WHEN EXTRACT(MONTH FROM traj_.date) IN ( 3, 4, 5)  THEN 'Spring'
        WHEN EXTRACT(MONTH FROM traj_.date) IN ( 6, 7, 8)  THEN 'Summer'
        WHEN EXTRACT(MONTH FROM traj_.date) IN ( 9,10,11)  THEN 'Fall'
        WHEN EXTRACT(MONTH FROM traj_.date) IN (12, 1, 2)  THEN 'Winter'
        ELSE 'Unknown'
    END AS season,
	count(traj_.id_traj) as No_traj_Human
FROM trajectories as traj_
inner join indiv_human  as ind_hu_
    on	ind_hu_.id_indiv = traj_.id_indiv
where traj_.count_points > traj_.count_missing_geom
and traj_.count_points > traj_.count_missing_temps
group by season
),
ani_ as (
SELECT
    CASE
        WHEN EXTRACT(MONTH FROM traj_.date) IN ( 3, 4, 5)  THEN 'Spring'
        WHEN EXTRACT(MONTH FROM traj_.date) IN ( 6, 7, 8)  THEN 'Summer'
        WHEN EXTRACT(MONTH FROM traj_.date) IN ( 9,10,11)  THEN 'Fall'
        WHEN EXTRACT(MONTH FROM traj_.date) IN (12, 1, 2)  THEN 'Winter'
        ELSE 'Unknown'
    END AS season,
	count(traj_.id_traj) as No_traj_Chamois
FROM trajectories as traj_
inner join recorded_animal  as ind_ani_
    on	ind_ani_.id_indiv = traj_.id_indiv
where traj_.count_points >= 24
group by season)

select hums_.*, ani_.No_traj_Chamois
from hums_
inner join ani_
	on hums_.season = ani_.season
ORDER BY
    CASE hums_.season
        WHEN 'Spring' THEN 1
        WHEN 'Summer' THEN 2
        WHEN 'Fall'   THEN 3
        WHEN 'Winter' THEN 4
        ELSE 5
    END
"""

table_8 = pd.read_sql_query(sql_query, con)
table_8

# %%
