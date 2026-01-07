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
with ec as (
-----Default-----
select '-' as Parameter_, 'Default' as Value_, count(*) as n_ec, null as n_ec_per
from """+head+"""encounter_default
-----doy_shift=0-----
union
select 'doy_shift' as Parameter_, '0' as Value_,count(*) as n_ec, round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_default
where abs(extract( doy from date_animal)-extract(doy from date_human)) <= 0
-----doy_shift=1-----
union
select 'doy_shift' as Parameter_, '1' as Value_, count(*) as n_ec, round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_default
where abs(extract( doy from date_animal)-extract(doy from date_human)) <= 1
-----doy_shift=2-----
union
select 'doy_shift' as Parameter_, '2' as Value_, count(*) as n_ec, round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_default
where abs(extract( doy from date_animal)-extract(doy from date_human)) <= 2
-----doy_shift=3-----
union
select 'doy_shift' as Parameter_, '3' as Value_, count(*) as n_ec, round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_default
where abs(extract( doy from date_animal)-extract(doy from date_human)) <= 3
-----doy_shift=14-----
union
select 'doy_shift' as Parameter_, '14' as Value_, count(*) as n_ec, round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_default
where abs(extract( doy from date_animal)-extract(doy from date_human)) <= 14
-----d_gap_a=None-----
union
select 'd_gap_a' as Parameter_, 'None' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_d_gap_a_none
-----d_gap_h None-----
union
select 'd_gap_h' as Parameter_, 'None' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_d_gap_h_none
-----HDAradius 500 m-----
union
select 'HDA_radius' as Parameter_, '500 m' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_hda_500
-----height_h 2 m-----
union
select 'height_h' as Parameter_, '2 m' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_human_2_m
-----height_a 0.8 m-----
union
select 'height_a' as Parameter_, '0.8 m' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_chamois_8_dm
-----height_a 1.2 m-----
union
select 'height_a' as Parameter_, '1.2 m' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_chamois_12_dm
-----t_gap 2 min-----
union
select 't_gap' as Parameter_, '2 min' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_t_gap_2_min
-----t_gap 4 min-----
union
select 't_gap' as Parameter_, '4 min' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_t_gap_4_min
-----t_gap 16 min-----
union
select 't_gap' as Parameter_, '16 min' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_t_gap_16_min
-----t_gap 2 hour-----
union
select 't_gap' as Parameter_, '2 hour' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_t_gap_2_h
-----t_gap 4 hour-----
union
select 't_gap' as Parameter_, '4 hour' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_t_gap_4_h
-----t_gap 24 hour-----
union
select 't_gap' as Parameter_, '24 hour' as Value_, count(*), round((count(*)-63270.0)/63270.0*100,1) as  n_ec_per
from """+head+"""encounter_t_gap_24_h
)



, ee as (
-----Default-----
select 1 as order_, '-' as Parameter_, 'Default' as Value_, count(*) as n_ee, null as  n_ec_per
from """+head+"""encounter_event_default
where vis_grid = true
and id_encounter is not null
-----doy_shift=0-----
union
select 2 as order_, 'doy_shift' as Parameter_, '0' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default as ee_
inner join """+head+"""encounter_default as ec_
	on ee_.id_encounter  = ec_.id_encounter
where ee_.vis_grid = true
and ee_.id_encounter is not null
and abs(extract( doy from date_animal)-extract(doy from date_human)) <= 0
-----doy_shift=1-----
union
select 3 as order_, 'doy_shift' as Parameter_, '1' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default as ee_
inner join """+head+"""encounter_default as ec_
	on ee_.id_encounter  = ec_.id_encounter
where ee_.vis_grid = true
and ee_.id_encounter is not null
and abs(extract( doy from date_animal)-extract(doy from date_human)) <= 1
-----doy_shift=2-----
union
select 4 as order_, 'doy_shift' as Parameter_, '2' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default as ee_
inner join """+head+"""encounter_default as ec_
	on ee_.id_encounter  = ec_.id_encounter
where ee_.vis_grid = true
and ee_.id_encounter is not null
and abs(extract( doy from date_animal)-extract(doy from date_human)) <= 2
-----doy_shift=3-----
union
select 5 as order_, 'doy_shift' as Parameter_, '3' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default as ee_
inner join """+head+"""encounter_default as ec_
	on ee_.id_encounter  = ec_.id_encounter
where ee_.vis_grid = true
and ee_.id_encounter is not null
and abs(extract( doy from date_animal)-extract(doy from date_human)) <= 3

-----doy_shift=14-----
union
select 6 as order_, 'doy_shift' as Parameter_, '14' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default as ee_
inner join """+head+"""encounter_default as ec_
	on ee_.id_encounter  = ec_.id_encounter
where ee_.vis_grid = true
and ee_.id_encounter is not null
and abs(extract( doy from date_animal)-extract(doy from date_human)) <= 14
-----d_gap_a=None-----
union
select 7 as order_, 'd_gap_a' as Parameter_, 'None' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_d_gap_a_none
where vis_grid = true
and id_encounter is not null
-----d_gap_h None-----
union
select 8 as order_, 'd_gap_h' as Parameter_, 'None' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_d_gap_h_none
where vis_grid = true
and id_encounter is not null
-----HDA_radius 500 m-----
union
select 9 as order_, 'HDA_radius' as Parameter_, '500 m' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_hda_500
where vis_grid = true
and id_encounter is not null
-----height_h 2 m-----
union
select 10 as order_, 'height_h' as Parameter_, '2 m' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default
where vis_grid_human_2_m = true
and id_encounter_human_2_m is not null
-----height_a 0.8 m-----
union
select 11 as order_, 'height_a' as Parameter_, '0.8 m' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default
where vis_grid_chamois_8_dm = true
and id_encounter_chamois_8_dm is not null
-----height_a 1.2 m-----
union
select 12 as order_, 'height_a' as Parameter_, '1.2 m' as Value_, count(*) as n_ec, round((count(*)-663389.0)/663389.0*100,1)  as  n_ec_per
from """+head+"""encounter_event_default
where vis_grid_chamois_12_dm = true
and id_encounter_chamois_12_dm is not null
-----t_gap 2 min-----
union
select 13 as order_, 't_gap' as Parameter_, '2 min' as Value_, null as n_ec, null as  n_ec_per
-----t_gap 4 min-----
union
select 14 as order_, 't_gap' as Parameter_, '4 min' as Value_, null as n_ec, null as  n_ec_per
-----t_gap 16 min-----
union
select 15 as order_, 't_gap' as Parameter_, '16 min' as Value_, null as n_ec, null as  n_ec_per
-----t_gap 2 hour-----
union
select 16 as order_, 't_gap' as Parameter_, '2 hour' as Value_, null as n_ec, null as  n_ec_per
-----t_gap 4 hour-----
union
select 17 as order_, 't_gap' as Parameter_, '4 hour' as Value_, null as n_ec, null as  n_ec_per
-----t_gap 24 hour-----
union
select 18 as order_, 't_gap' as Parameter_, '24 hour' as Value_, null as n_ec, null as  n_ec_per
)

select ee.*, ec.n_ec, ec.n_ec_per
from ee
full join ec
	on ee.value_ = ec.value_
	and ee.parameter_ = ec.parameter_
order by ee.order_

"""

table_6 = pd.read_sql_query(sql_query, con)
table_6

# %%
