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

# %% Default: Create Encounter Events  
# Default: Create Encounter  Events  

my_utils.Encounter_events(
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
        db = db,
        db_user     = db_user,
        db_password = db_password,
        where = where)

# %% HDA = 500: Create Encounter Events 
# HDA = 500: Create Encounter Events

HDA_radius  = 500
tail_HDA_500 = '_HDA_500'

tracks, tracks_simp_new_filter, id_traj = my_utils.create_filltered_hda_table(
                                                        head+'traj_ints'+tail, 
                                                        head, 
                                                        tail_HDA_500, 
                                                        HDA_radius, 
                                                        esp = min_dist, 
                                                        db = db, 
                                                        db_user = db_user, 
                                                        db_password = db_password,
                                                        cells = [], 
                                                        bbox = bbox, 
                                                        bbox_grid = [],
                                                        time_max=min_time)

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

qurry = """\
        COMMENT ON TABLE """ + head + """hda""" + tail_HDA_500+ """ IS 
        'source_table   =  """ + str(head+'traj_ints'+tail) + """
        shift       = """+ str(shift) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

source_ppa      =  head+'ppa'+tail
source_hda      =  head+'hda'+tail_HDA_500 
source_pairing  =  head+'traj_ints'+tail

start = time.time()

my_utils.create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail_HDA_500, 
                            comp_type = 'geom', 
                            db = db, 
                            db_user = db_user, 
                            db_password = db_password)

ee_length = time.time()-start

print(ee_length)

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

# adds comments to table saving the parameter used for the table
qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail_HDA_500+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa   = """+ str(source_ppa) + """
        source_hda   = """+ str(head+'hda'+tail_HDA_500) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        duration    = """+ str(ee_length)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

HDA_radius = 250

print('------WAIT Visibility Check should be run in QGIS Before proceeding------')


# %% d_gap_a = 999999999: Create Encounter Events
# d_gap_a = 999999999: Create Encounter Events

d_gap_a = 999999999
tail_d_gap_a_none    = '_d_gap_a_none'

source_table = head+'traj_ints'+tail

my_utils.create_ppa_table(source_table, 
                          head, 
                          tail_d_gap_a_none, 
                          db = db, 
                          db_user = db_user, 
                          db_password = db_password,
                          d_gap_a = d_gap_a,
                          bbox=bbox)

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

qurry = """\

        COMMENT ON TABLE """ + head + """close_points_animal""" + tail_d_gap_a_none + """ IS
        
        'source_table   = """+ str(source_table) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """';

        
        COMMENT ON TABLE """ + head + """ppa""" + tail_d_gap_a_none + """ IS
        
        'source_table   = """+ str(source_table) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """';

        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()


source_ppa      =  head+'ppa'+tail_d_gap_a_none
source_hda      =  head+'hda'+tail
source_pairing  =  head+'traj_ints'+tail

start = time.time()

my_utils.create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail_d_gap_a_none, 
                            comp_type = 'geom', 
                            db = db, 
                            db_user = db_user, 
                            db_password = db_password)

ee_length = time.time()-start 

print(ee_length)

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

# adds comments to table saving the parameter used for the table
qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail_d_gap_a_none+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa  = """+ str(head+'ppa'+tail_d_gap_a_none) + """
        source_hda  = """+ str(source_hda) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ +str(1.25) + """
        d_gap_a     = """ +str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        duration    = """+ str(ee_length)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

d_gap_a = 500

# %% d_gap_h = 999999999: Create Encounter Events
# d_gap_h = 999999999: Create Encounter Events

d_gap_h = 999999999
tail_d_gap_h_none    = '_d_gap_h_none'

source_table = head+'traj_ints'+tail

tracks, tracks_simp_new_filter, id_traj = my_utils.create_filltered_hda_table(
                                                        source_table, 
                                                        head, 
                                                        tail_d_gap_h_none, 
                                                        HDA_radius, 
                                                        esp = min_dist, 
                                                        db = db,
                                                        db_user = db_user, 
                                                        db_password = db_password, 
                                                        cells = [],
                                                        d_gap_h = d_gap_h, 
                                                        bbox = bbox, 
                                                        bbox_grid = [],
                                                        time_max=min_time)

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

qurry = """\
        COMMENT ON TABLE """ + head + """hda""" + tail_d_gap_h_none+ """ IS 
        'source_table   =  """ + str(source_table) + """
        shift       = """+ str(shift) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

source_ppa      =  head+'ppa'+tail
source_hda      =  head+'hda'+tail_d_gap_h_none
source_pairing  =  head+'traj_ints'+tail

start = time.time()

my_utils.create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail_d_gap_h_none, 
                            comp_type = 'geom', 
                            db = db, 
                            db_user = db_user, 
                            db_password = db_password)

ee_length = time.time()-start 

print(ee_length)

conn = psycopg2.connect(database= db , user=db_user)

curs = conn.cursor()

# adds comments to table saving the parameter used for the table
qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail_d_gap_h_none+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa   = """+ str(source_ppa) + """
        source_hda   = """+ str(head+'HDA'+tail_d_gap_h_none) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        duration    = """+ str(ee_length)+"""'; 
        """

curs.execute(qurry)

conn.commit()
curs.close()
conn.close()

d_gap_h = 500
