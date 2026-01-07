#%%

from sqlalchemy import create_engine, text
import pandas as pd

# Create an engine that connects to your database
db          =  'ResRoute'
db_user     =  'postgres'
db_password =  'postgres'
db_connection_url = "postgresql://"+db_user+":"+db_password+"@localhost:5432/"+db
con = create_engine(db_connection_url)

head = 'exp__'

# %%
# SQL query combining all the queries you provided
sql_query = """
with EE_ as (
select 1 as order_, count(*) as N_EE
from """+head+"""encounter_event_default
where vis_grid = true
union
select 2 as order_, count(*) as N_EE
from """+head+"""encounter_event_hda_500
where vis_grid = true
union
select 3 as order_, count(*) as N_EE
from """+head+"""encounter_event_default
),
EC_ as (
select 1 as order_, count(*) as N_EC, avg(latest-earliest) as ec_d_t, avg(st_area(eca_a)) as eca_a_area, avg(st_area(eca_h)) as eca_h_area
from """+head+"""encounter_default
union
select 2 as order_, count(*) as N_EC, avg(latest-earliest) as ec_d_t, avg(st_area(eca_a)) as eca_a_area, avg(st_area(eca_h)) as eca_h_area
from """+head+"""encounter_hda_500
union
select 3 as order_, count(*) as N_EC, avg(latest-earliest) as ec_d_t, avg(st_area(eca_a)) as eca_a_area, avg(st_area(eca_h)) as eca_h_area
from """+head+"""encounter_ignore_vis
)

select  EE_.*, EC_.*
from EE_
full join EC_
	on EE_.order_ = EC_.order_
order by EE_.order_

"""

table_5 = pd.read_sql_query(sql_query, con)
table_5

# %%
