# %% Import library
# Import library

import sys
import os

tracklib_folder_path = '!! ADD FILE PATH HERE !!'
db          = 'ResRoute'
db_user     = 'postgres'
db_password = 'postgres'


if tracklib_folder_path not in sys.path:
    sys.path.insert(0, tracklib_folder_path)
    
import time 
from tracklib.core.obs_time import ObsTime
from tracklib.core import bbox
import my_utils
import psycopg2
import numpy as np

ObsTime.setReadFormat("4Y-2M-2DT2h:2m:2sZ")

head        = 'exp__'
tail        = '_Default'
shift       = 15
max_speed   = 1.25  #Does not update
d_gap_a     = 500
min_dist    = 25
min_time    = 60
HDA_radius  = 250
d_gap_h     = 500
height_h    = 1.6   # Does not update!!! must update in QGIS code saves value in table comments
height_a    = 1     # Does not update!!! must update in QGIS code saves value in table comments
t_gap       = 8 * 60     
ECA_h_radius= 10
where       = "select id_indiv from indiv_human"

x_min = 942749.5
x_max = 958749.5
y_min = 6504411.5
y_max = 6520411.5

bbox = [x_min,x_max,y_min,y_max]


# %% Default: Create Encounters
# Default: Create Encounters
my_utils.Encounters(
        bbox,
        head,
        tail,
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h,
        height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap,     
        ECA_h_radius,
        db,
        db_user,
        db_password,
        where)

# %% HDA = 500: Create Encounters 
# HDA = 500: Create Encounters
my_utils.Encounters(
        bbox,
        head,
        '_hda_500',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius = 500,
        d_gap_h=d_gap_h,
        height_h=height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a=height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap=t_gap,     
        ECA_h_radius=ECA_h_radius,
        db=db,
        where=where,
        source_table    = head +'encounter_event_hda_500',
        source_pairing  = head +'traj_ints_default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_500',
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% d_gap_h = None: Create Encounters  
# d_gap_h = None: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_d_gap_h_none',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = 999999999,
        height_h=height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a=height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap=t_gap,     
        ECA_h_radius=ECA_h_radius,
        db=db,
        where=where,
        source_table    = head +'encounter_event_d_gap_h_none',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_Default',
        source_hda      = head +'hda_d_gap_h_none',
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% d_gap_a = None: Create Encounters 
# d_gap_a = None: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_d_gap_a_none',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = 999999999,
        height_h=height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a=height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap=t_gap,     
        ECA_h_radius=ECA_h_radius,
        db=db,
        where=where,
        source_table    = head +'encounter_event_d_gap_a_none',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_d_gap_a_none',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% t_gap = 2 min: Create Encounters 
# t_gap = 2 min: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_2_min',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 2*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_t_gap_2_min',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% t_gap = 4 min: Create Encounters 
# t_gap = 4 min: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_4_min',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 4*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_t_gap_4_min',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% t_gap = 16 min: Create Encounters 
# t_gap = 16 min: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_16_min',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 16*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_t_gap_16_min',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% t_gap = 2 hours: Create Encounters 
# t_gap = 2 hours: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_2_h',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 2*60*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_t_gap_2_h',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% t_gap = 4 hours: Create Encounters 
# t_gap = 4 hours: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_4_h',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 4*60*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_t_gap_4_h',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% t_gap = 24 hours: Create Encounters 
# t_gap = 24 hours: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        '_t_gap_24_h',
        shift,
        max_speed,  #Does not update
        d_gap_a,
        min_dist,
        min_time,
        HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = 24*60*60,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_t_gap_24_h',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid')

# %% height_chamois = 0.8 m: Create Encounters 
# height_chamois = 0.8 m: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        tail = '_chamois_8_dm',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = 0.8,          # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_chamois_8_dm',
        vis_column      = 'vis_grid_chamois_8_dm',
        vis_table       = 'vis_grid_chamois_8_dm')

# %% height_chamois = 1.2 m: Create Encounters 
# height_chamois = 1.2 m: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        tail = '_chamois_12_dm',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = 1.2,          # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_chamois_12_dm',
        vis_column      = 'vis_grid_chamois_12_dm',
        vis_table       = 'vis_grid_chamois_12_dm')


# %% height_human = 2 m: Create Encounters
# height_human = 2 m: Create Encounters 

my_utils.Encounters(
        bbox,
        head,
        tail = '_human_2_m',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = 2,                 # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,          # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_human_2_m',
        vis_column      = 'vis_grid_human_2_m',
        vis_table       = 'vis_grid_human_2_m')



# %% Ignoring intervisibility: Create Encounters
# Ignoring intervisibility: Create Encounters 

source_table = head + """encounter_event""" + tail

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

qurry = """\

        ALTER TABLE """ + source_table + """ DROP IF EXISTS vis_grid_all_true;
        
        ALTER TABLE """ + source_table + """
        ADD vis_grid_all_true BOOLEAN NOT NULL DEFAULT TRUE;

     """
curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

my_utils.Encounters(
        bbox,
        head,
        tail = '_ignore_vis',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = HDA_radius,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_Default',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_500',
        id_column       = 'id_encounter_ignore_vis',
        vis_column      = 'vis_grid_all_true',
        vis_table       = None # Skips joining visibility
        )



# %% Ignoring intervisibility hda = 500: Create Encounters
# Ignoring intervisibility hda = 500: Create Encounters 

source_table = head + """encounter_event_hda_500"""

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

qurry = """\

        ALTER TABLE """ + source_table + """ DROP IF EXISTS vis_grid_all_true;
        
        ALTER TABLE """ + source_table + """
        ADD vis_grid_all_true BOOLEAN NOT NULL DEFAULT TRUE;

     """
curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

my_utils.Encounters(
        bbox,
        head,
        tail = '_ignore_vis_hda_500',
        shift = shift,
        max_speed = max_speed,  #Does not update
        d_gap_a = d_gap_a,
        min_dist = min_dist,
        min_time = min_time,
        HDA_radius = 500,
        d_gap_h = d_gap_h,
        height_h = height_h,     # Does not update!!! must update in QGIS code saves value in table comments
        height_a = height_a,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap = t_gap,     
        ECA_h_radius= ECA_h_radius,
        db = db,
        where = where,
        source_table    = head +'encounter_event_hda_500',
        source_pairing  = head +'traj_ints_Default',
        source_ppa      = head +'ppa_default',
        source_hda      = head +'hda_default',
        id_column       = 'id_encounter_ignore_vis',
        vis_column      = 'vis_grid_all_true',
        vis_table       = None # Skips joining visibility
        )



# %%
