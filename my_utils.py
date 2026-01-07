# %%
import sys
import math
import shapely as shp
import psycopg2
import numpy as np
from typing import Union
import time 
import warnings

import sys
import os

folder_path = r"ADD PATH TO TRACKLIB FOLDER e.x. => \tracklib"

if folder_path not in sys.path:
    sys.path.insert(0, folder_path)

import tracklib as tkl
from tracklib.core import track as tk
from tracklib.core import track_collection
from tracklib.core import Obs
from tracklib.core import ObsTime
from tracklib.core import ENUCoords
from tracklib.core import makeCoords

# %%
class WrongArgumentError(Exception):
    pass

def encounter_events(
        bbox,
        head        = '',
        tail        = '',
        shift       = 15,
        max_speed   = 1.25,  #Does not update
        d_gap_a     = 500,
        min_dist    = 25,
        min_time    = 60,
        HDA_radius  = 250,
        d_gap_h     = 500,
        height_h    = 1.6,  # Does not update!!! must update in QGIS code saves value in table comments
        height_a    = 1,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap       = 8 * 60,     
        ECAh_radius = 10,
        db          = 'ResRoute',
        db_user     = 'postgres',
        db_password = 'postgres',
        where       = ''):
    
    start_time = time.time()
    print('Running find_comparable_routes')
    start_find_comparable_routes = time.time()
    find_comparable_routes(where, shift, head, tail, db = db, db_user = db_user, db_password = db_password)
    print('find_comparable_routes took '+str(time.time() - start_find_comparable_routes)+' seconds')

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
        COMMENT ON TABLE 
        """ + head + """traj_ints""" + tail + """ 
        IS 
        
        'shift =  """ + str(shift) + """';
        
        """
    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

    source_table = head+'traj_ints'+tail

    print('Running create_ppa_table')
    start_create_ppa_table = time.time()
    create_ppa_table(source_table, head, tail, db = db, db_user = db_user, db_password = db_password, bbox=bbox, d_gap_a = d_gap_a)
    print('create_ppa_table took '+str(time.time()-start_create_ppa_table)+' seconds')

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\

        COMMENT ON TABLE """ + head + """close_points_animal""" + tail + """ IS
        
        'source_table   = """+ str(source_table) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """';

        
        COMMENT ON TABLE """ + head + """ppa""" + tail + """ IS
        
        'source_table   = """+ str(source_table) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """';

        """

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

    source_table = head+'traj_ints'+tail

    print('Running create_filltered_hda_table')
    start_create_filltered_hda_table = time.time()
    tracks, tracks_simp_new_filter, id_traj = create_filltered_hda_table(
                                                        source_table, 
                                                        head, 
                                                        tail, 
                                                        db = db, 
                                                        db_user = db_user, 
                                                        db_password = db_password, 
                                                        buffer_size = HDA_radius, 
                                                        esp = min_dist,
                                                        d_gap_h = d_gap_h, 
                                                        #mode = 1, 
                                                        cells = [], 
                                                        bbox = bbox, 
                                                        bbox_grid = [],
                                                        time_max=min_time)
    print('create_filltered_hda_table took '+str(time.time()-start_create_filltered_hda_table)+' seconds')

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
        COMMENT ON TABLE """ + head + """hda""" + tail+ """ IS 
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

    source_ppa       =  head+'ppa'+tail
    source_hda       =  head+'hda'+tail
    source_pairing   =  head+'traj_ints'+tail

    print('Running create_encounter_events')
    start_create_encounter_events = time.time()
    create_encounter_events(source_ppa, 
                            source_hda, 
                            source_pairing,
                            head, 
                            tail, 
                            comp_type = 'geom', 
                            db = db, 
                            db_user = db_user, 
                            db_password = db_password)
    print('create_encounter_events took '+str(time.time()-start_create_encounter_events)+' seconds')



    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    # adds comments to table saving the peremiters used for the table
    qurry = """\
        COMMENT ON TABLE """ + head + """encounter_event""" + tail+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ppa   = """+ str(source_ppa) + """
        source_hda   = """+ str(source_hda) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     =  """ + str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""'; 
        """

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()
    print('Finished total run time: '+ str(time.time() - start_time)+ ' seconds')
    print('------WAIT Visibility Check should be run in QGIS Before proceeding------')

def Encounters(
        bbox,
        head        = '',
        tail        = '',
        shift       = 15,
        max_speed   = 1.25,  #Does not update
        d_gap_a     = 500,
        min_dist    = 25,
        min_time    = 60,
        HDA_radius  = 250,
        d_gap_h     = 500,
        height_h    = 1.6,   # Does not update!!! must update in QGIS code saves value in table comments
        height_a    = 1,     # Does not update!!! must update in QGIS code saves value in table comments
        t_gap       = 8 * 60,     
        ECA_h_radius = 10,
        db          = 'ResRoute',
        db_user     = 'postgres',
        db_password = 'postgres',
        where       = '',
        source_table    = None,
        source_pairing  = None,
        source_ppa      = None,
        source_hda      = None,
        id_column       = 'id_encounter',
        vis_column      = 'vis_grid',
        vis_table       = 'vis_grid'):

    start_time = time.time()

    if not source_table:
        source_table   = head+'encounter_event'+tail
    if vis_table:
        print('Running join_vis_to_encounter_events')
        print('vis_table : '+ str(vis_table))
        print('vis_column : '+ str(vis_column))

        start_join_vis_to_encounter_events = time.time()
        join_vis_to_encounter_events(source_table,
                                    vis_table, 
                                    db = db, 
                                    db_user = db_user, 
                                    db_password = db_password,
                                    vis_column = vis_column)
        print('join_vis_to_encounter_events took '+str(time.time()-start_join_vis_to_encounter_events)+' seconds')
    elif vis_table is None:
        print('Skipping join_vis_to_encounter_events')
    else:
        print('error vis_table entery is unexpected neither is or not')


    print('Running assign_encounters_SQL')
    start_assign_encounters_SQL = time.time()
    assign_encounters_SQL(source_table, 
                          t_gap,  
                          db = db, 
                          db_user = db_user, 
                          db_password = db_password,  
                          id_column = id_column, 
                          vis_column = vis_column)
    print('assign_encounters_SQL took '+str(time.time()-start_assign_encounters_SQL)+' seconds')

    if not source_pairing:
        source_pairing = head+'traj_ints'+tail

    if not source_ppa:    
        source_ppa     = head+'ppa'+tail
    
    if not source_hda:
        source_hda     = head+'hda'+tail


    print('Running create_encounter_table')
    start_create_encounter_table= time.time()
    create_encounter_table(source_table, 
                           source_pairing, 
                           head, 
                           tail,  
                           db = db, 
                           db_user = db_user, 
                           db_password = db_password, 
                           id_column  = id_column, 
                           vis_column = vis_column,
                           ppa_table  = source_ppa,
                           ECA_h_radius = ECA_h_radius)
    print('create_encounter_table took '+str(time.time()-start_create_encounter_table)+' seconds')
    if not source_hda:
        source_hda     = head+'hda'+tail

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
        COMMENT ON TABLE """ + head + """encounter""" + tail+ """ IS 
        'source_pairs   =  """ + str(source_pairing) + """
        source_ee   = """+ str(source_table) + """
        source_ppa  = """+ str(source_ppa) + """
        source_hda  = """+ str(source_hda) + """
        shift       = """ +str(shift)+ """
        max_speed   = """ + str(1.25) + """
        d_gap_a     = """ + str(d_gap_a) + """
        min_dist    = """+ str(min_dist) + """
        min_time    = """+ str(min_time)+ """
        HDA_radius  = """+ str(HDA_radius) + """
        d_gap_h     = """+ str(d_gap_h)+"""
        id_column   = """+ str(id_column)+"""
        ECA_h_radius= """+ str(ECA_h_radius)+"""'; 
        """
    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()
    print('Finished total run time: '+ str(time.time() - start_time)+ ' seconds')

def find_comparable_routes(where, shift, head, tail, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres'):
    
    """
    Identifies and stores candidate human-animal trajectory pairs for encounter detection.

    This function should be called first in the encounter detection workflow. It creates 
    and populates a table in the specified SQL database with trajectory pairs (human and animal) 
    that are close enough in time to be considered potential encounters. The resulting table 
    is used by subsequent functions for more detailed analysis.

    Parameters
    ----------
    values : dict
        A dictionary containing the following keys:
    
        - 'Where': str  
            Custom SQL WHERE clause to filter data sources (e.g., species, location, etc.).
        
        - 'Shift': int  
            Maximum difference in day-of-year (DOY) allowed between human and animal 
            trajectories for comparison.
        
        - 'head': str  
            Optional prefix to be added to the output table name (useful for testing).
        
        - 'tail': str  
            Optional suffix to be added to the output table name.
        
        - 'db': str  
            Name or path of the SQL database to update.

    Returns
    -------
    None
        This function does not return anything in Python. It creates a new table 
        in the linked database with candidate trajectory pairs for encounter analysis.

    The created table includes the following columns:
        - id_encounter: INTEGER PRIMARY KEY
        - earliest: TIMESTAMP
        - latest: TIMESTAMP
        - date_animal: DATE
        - date_human: DATE
        - min_dist: NUMERIC
        - vis: BOOLEAN
    """
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\

     DROP TABLE IF EXISTS  """ + head + """traj_ints""" + tail + """;

     select 
          a_.id_traj as id_traj_1,
          b_.id_traj as id_traj_2, 
          a_.date as date_1, 
          b_.date as date_2,
          a_.start_time_1 as start_time_1,
          a_.end_time_1 as end_time_1,
          b_.start_time_2 as start_time_2,
          b_.end_time_2 as end_time_2
     into """ + head +"""traj_ints""" + tail + """
     from (
          select trajectories.* , min(sub_trajectories.start_time) as start_time_1, max(sub_trajectories.end_time ) as end_time_1
          from trajectories
          left join sub_trajectories 
          on sub_trajectories.id_traj = trajectories.id_traj
          where id_indiv in 
               (select id_indiv from trajectories_indivs where type_indiv = 'animal')
          group by trajectories.id_traj, sub_trajectories.id_traj
     ) as a_

     inner join (
          select trajectories.* , min(sub_trajectories.start_time) as start_time_2, max(sub_trajectories.end_time ) as end_time_2
          from trajectories
          left join sub_trajectories 
          on sub_trajectories.id_traj = trajectories.id_traj
          where id_indiv in 
               (select id_indiv from trajectories_indivs where type_indiv = 'human')
          and id_indiv in 
               ("""+where+""")
          and trajectories.id_traj != 15059
          group by trajectories.id_traj, sub_trajectories.id_traj
     ) as b_
               
     on  extract(doy  from a_.date) <= extract(doy from b_.date)+ """+ str(shift)+ """
     and extract(doy from a_.date) >= extract(doy from b_.date)- """+ str(shift) +"""

     where a_.count_points-a_.count_missing_geom-a_.count_outlier >= 24
     and (a_.start_time_1 >= b_.start_time_2 
     and a_.start_time_1 <= b_.end_time_2
          
     or   b_.start_time_2 >= a_.start_time_1 
     and  b_.start_time_2 <= a_.end_time_1
          
     or   a_.end_time_1 >= b_.start_time_2 
     and  a_.end_time_1 <= b_.end_time_2
          
     or   b_.end_time_2 >= a_.start_time_1 
     and  b_.end_time_2 <= a_.end_time_1);
     
    DROP INDEX IF EXISTS """ + head + """idx_traj_ints_id_traj_2""" + tail+ """;
    DROP INDEX IF EXISTS """ + head + """idx_traj_ints_id_traj_1""" + tail+ """;

    CREATE INDEX """ + head + """idx_traj_ints_id_traj_2""" + tail+ """ ON """ + head + """traj_ints""" + tail+ """(id_traj_2);
    CREATE INDEX """ + head + """idx_traj_ints_id_traj_1""" + tail+ """ ON """ + head + """traj_ints""" + tail+ """(id_traj_1);
    """
    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

def create_ppa_table(source_table, head, tail, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', buffer_size = 0, cells = [], bbox = [], bbox_grid = [], d_gap_a = '500'):
    """
    Extracts and stores Potential Path Areas (PPAs) for animal trajectory pairs.

    This function should be called after `find_comparable_routes`. It creates and populates
    a table in the specified SQL database containing Potential Path Areas (PPAs) derived
    from pairs of points in animal trajectories that may be part of an encounter event.

    These PPAs are used in later analysis to evaluate possible overlap or proximity between
    animal and human trajectories.

    Parameters
    ----------
    values : dict
        A dictionary containing the following keys:

        - 'source_table' : str  
            Name of the table containing candidate encounter events, typically created by 
            `find_comparable_routes`.

        - 'head' : str, optional  
            Optional prefix to add to the output table name (useful for testing or versioning).

        - 'tail' : str, optional  
            Optional suffix to add to the output table name.

        - 'db' : str  
            Path or name of the SQL database to update.

        - 'd_gap_a' : int  
            Maximum allowed distance between consecutive points in an animal trajectory.
            Trajectory segments exceeding this threshold will be excluded from PPA generation.

    Returns
    -------
    None
        This function does not return a Python object. It creates a new SQL table
        in the specified database containing the generated PPAs.

    The created table includes the following columns:

        - id_point             : INTEGER
        - temps                : TIME WITHOUT TIME ZONE
        - geom                 : GEOMETRY
        - id_sub_traj          : INTEGER
        - id_traj              : INTEGER
        - date                 : DATE
        - next_id_point        : INTEGER
        - next_temps           : TIME WITHOUT TIME ZONE
        - next_geom            : GEOMETRY
        - next_id_sub_traj     : INTEGER
        - next_id_traj         : INTEGER
        - ppa                  : GEOMETRY
        - x_grid               : INTEGER
        - y_grid               : INTEGER
        - x_coord              : DOUBLE PRECISION
        - y_coord              : DOUBLE PRECISION
    """

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
    
    DROP TABLE IF EXISTS """ + head + """ppa""" + tail+ """;
    DROP TABLE IF EXISTS """ + head + """close_points_animal""" + tail+ """;

    SELECT 
        DISTINCT p.*,
        FLOOR((st_x(p.geom) - 942749.5) / 25) as x_grid,
        FLOOR((st_y(p.geom) - 6504411.5) / 25) as y_grid,
        ti.id_traj_1 as id_traj,
        ti.date_1
    into """ + head + """close_points_animal""" + tail+ """
    FROM """ + source_table + """ ti
    LEFT JOIN sub_trajectories st ON st.id_traj = ti.id_traj_1
    LEFT JOIN points p ON p.id_sub_traj = st.id_sub_traj
    WHERE p.outlier = 'false'
    AND p.geom IS NOT NULL
    ORDER BY ti.id_traj_1, p.id_point, p.temps;

    alter table """ + head + """close_points_animal""" + tail+ """
    add ppa geometry;

    alter table """ + head + """close_points_animal""" + tail+ """
    add primary key (id_point)

    """

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    #print('close_points_animal table initialized')

    qurry = """\
        SELECT id_point, id_traj, temps,  st_x(geom), st_y(geom)
        FROM """ + head + """close_points_animal""" + tail+ """
        order by id_traj, temps
        """

    curs.execute(qurry)

    id_point_lst = []

    #print('close_points_animal data pulled')

    tracks = track_collection.TrackCollection()
    trace  = tk.Track([],1)

    LINES = curs.fetchall()
    trace.tid = LINES[0][1]

    for row in LINES:
        id_traj = row[1]

        if id_traj != trace.tid:
            if trace is None:
                continue
            if trace.size() <= 0:
                continue
            #(len(trace))
            trace.createAnalyticalFeature('id_point', id_point_lst)
            tracks.addTrack(trace)
            id_point_lst = []
            trace = tk.Track([],1)
            trace.tid = id_traj

        id_point_lst.append(row[0])
        trace.addObs(Obs(ENUCoords(row[3],row[4],-1),tk.ObsTime.readTimestamp(str(row[2]))))

    #print('Data placed in track collection')
    #print('Building PPA')
    tracks.addAnalyticalFeature(add_ppa)
    #print('PPA Finished')

    d = list(zip(
        tracks.getAnalyticalFeature('add_ppa'),
        tracks.getAnalyticalFeature('id_point')
    ))

    #print('Adding PPA to Database')

    curs.executemany("""
        update """ + head + """close_points_animal""" + tail+ """
            set ppa = ST_GeomFromWKB(%s::geometry, 2154) 
            where id_point = %s 
                """,d)

    #print('Finished database update')

    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\

    DROP INDEX IF EXISTS """ + head + """idx_sub_traj_temps_ppa""" + tail+ """;
    DROP INDEX IF EXISTS """ + head + """idx_id_traj_ppa""" + tail+ """;


    CREATE INDEX """ + head + """idx_sub_traj_temps_ppa""" + tail+ """ ON """ + head + """close_points_animal""" + tail+ """(id_sub_traj, temps);
    CREATE INDEX """ + head + """idx_id_traj_ppa""" + tail+ """        ON """ + head + """close_points_animal""" + tail+ """(id_traj);"""

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()
    
    qurry = 'DROP TABLE IF EXISTS ' + head + 'ppa' + tail+ ';'
    curs.execute(qurry)


    variables = """\
        id_point 	        integer, \n
        temps               time without time zone,\n
        geom                geometry,\n
        id_sub_traj         integer, \n
        id_traj             integer, \n
        date                date,\n
        next_id_point       integer, \n
        next_temps          time without time zone,\n
        next_geom           geometry,\n
        next_id_sub_traj    integer, \n
        next_id_traj        integer, \n
        ppa                 geometry,\n
        x_grid              integer,\n
        y_grid              integer,\n
        x_coord				double precision,
        y_coord 			double precision
        """
    #print('PPA table created')
    
    table_name = head + 'ppa' + tail
    if not cells:
        #print('Skipping Partitioning')

        qurry = """\
                create table """ + table_name + """ (
                """+ variables +"""
                );
                """
        curs.execute(qurry)
        conn.commit()

    elif cells:
        #print('Starting Partitioning')

        bb_1_list_ppa,_ = table_partitioning(table_name, 
                   variables, 
                   'x_grid', 
                   'y_grid', 
                   bbox_grid, 
                   cells, 
                   cells,
                   db)
        
    #print('Starting PPA Data Insertions')

    qurry = """\
    insert into """ + head + """ppa""" + tail+ """
    select 
        id_point, 
        temps::time as temps, 
        geom, 
        id_sub_traj, 
        id_traj,
        date_1 as date,
        LEAD(id_point) OVER (ORDER BY id_sub_traj, temps) AS next_id_point,
        LEAD(temps::time) OVER (ORDER BY id_sub_traj, temps) AS next_temps,
        LEAD(geom) OVER (ORDER BY id_sub_traj, temps) AS next_geom,
        LEAD(id_sub_traj) OVER (ORDER BY id_sub_traj, temps) AS next_id_sub_traj,
        LEAD(id_traj) OVER (ORDER BY id_sub_traj, temps) AS next_id_traj,
        ppa,
        x_grid,
        y_grid,
        st_x(geom) as x_coord,
        st_y(geom) as x_coord
    from """ + head + """close_points_animal""" + tail+ """
    WHERE  geom 
                && -- intersects,  gets more rows  -- CHOOSE ONLY THE
                ST_MakeEnvelope (
                    """+ str(bbox[0]) +""",
                    """+ str(bbox[2]) +""",
                    """+ str(bbox[1]) +""",
                    """+ str(bbox[3]) +""",
                    2154)
    order by id_sub_traj, temps;

    alter table """ + head + """ppa""" + tail+ """
    add geom_line geometry;

    update """ + head + """ppa""" + tail+ """ 
    set geom_line = st_makeline(geom,next_geom);

    delete from """ + head + """ppa""" + tail+ """
    where st_length(geom_line) >= """ + str(d_gap_a) + """;

    delete from """ + head + """ppa""" + tail+ """
    where id_traj != next_id_traj;

    delete from """ + head + """ppa""" + tail+ """
    where next_id_traj is null;

    alter table """ + head + """ppa""" + tail+ """
    add buffer geometry;  
    
    CREATE INDEX """ + head + """ppa_index""" + tail+ """
        ON """ + head + """ppa""" + tail+ """
        USING GIST (ppa);

    -- Create an index on the time part of the 'temps' column in the 'ppa' table
    CREATE INDEX """ + head + """ppa_triple_index""" + tail+ """ ON """ + head + """ppa""" + tail+ """ (id_traj, temps, next_temps);
    
    -- Create index on 'id_traj' column in 'ppa' table
    CREATE INDEX """ + head + """idx_id_traj__ppa""" + tail+ """ ON """ + head + """ppa""" + tail+ """(id_traj);

    CREATE INDEX """ + head + """idx_ppa_grid""" + tail+ """ ON """ + head + """ppa""" + tail+ """(x_grid,y_grid);    

    """

    curs.execute(qurry)
    
    conn.commit()
    curs.close()
    conn.close() 
    #print('---Create PPA Finished---')

def add_ppa(track, i):
    """
    Adds Potential Path Area (PPA) geometry to GPS trajectory points.

    This function is typically called by `create_ppa_table` to augment animal GPS tracks
    with PPA geometry information for further spatial analysis.

    Parameters
    ----------
    track : object
        The trajectory object that will be enhanced by adding Potential Path Area (PPA) geometry.
    Returns
    -------
    None
        This function does not return a Python object. It adds PPA geometry to GPS tracks 
        for later insertion into the SQL database.
    """


    ##print(track.tid)
    if i == track.size()-1:
        return shp.Point(0, 0).wkb
    
    x1=track.getX(i)
    y1=track.getY(i)
    t1=track.getT(i)
    x2=track.getX(i+1)
    y2=track.getY(i+1)
    t2=track.getT(i+1)

    ds = track.getObs(i).distance2DTo(track.getObs(i + 1))
 
    dx = x2-x1
    dy = y2-y1
    dt = t2-t1
    
    speed = 1.25 * ds/(dt+0.00000000000001) 
        # the major axis of the PPA ellipse based on input speed (in time geography this speed is max speed)
    major = dt * speed
    minor: float = (major ** 2 - ds ** 2) ** 0.5  # calculate minor axis for the ellipse
        
    if dy == 0:
        dy = 0.1
    if dx == 0:
        dx = 0.1
        
    angle: float = np.rad2deg(math.atan(abs(dy / dx)))  # angle of the ellipse
        
    if dx * dy < 0:
            # the rotation angle of the PPA ellipse in 2nd and 4th quadrants
        angle = 180 - angle
    center = [(x1+x2)/2 ,(y1+y2)/2]

    #p = ellipse_polyline(center, major, minor, angle, 100)
    n=25
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)  # Return evenly spaced numbers over a specified interval

    st = np.sin(t)
    ct = np.cos(t)

    angle = np.deg2rad(angle)  # rotation angle of ellipse in radius unit
    sa = np.sin(angle)
    ca = np.cos(angle)

    p = np.empty((n, 2))

    expr_x = center[0] + major / 2.0 * ca * ct - minor / 2.0 * sa * st
    expr_y = center[1] + major / 2.0 * sa * ct + minor / 2.0 * ca * st

    if np.iscomplexobj(expr_x) or np.iscomplexobj(expr_y):
    #    raise ValueError(f"Complex value generated for track.id = {track.tid}")
        return shp.Point(0, 0).wkb

    p[:, 0] = expr_x
    p[:, 1] = expr_y


    return shp.Polygon(shp.LinearRing(p)).wkb

def table_partitioning(table_name, variables, x_parition, y_partition, bbox, x_cells, y_cells, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres'):
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)
    curs = conn.cursor()

    qurry = """\
        create table """ + table_name + """ (
        """+ variables +"""
        )PARTITION BY RANGE ("""+ x_parition +""");
        """
    ##print(qurry)

    curs.execute(qurry)

    x_breaks = np.linspace(bbox[0],bbox[1], x_cells+1)
    y_breaks = np.linspace(bbox[2],bbox[3], y_cells+1)

    bb_list = []
    bb_1_list = []
    bb_2_list = []

    for i in range(len(x_breaks)-1):
        ##print("---"+str(i)+"---")
        qurry = """\
            create table """ + table_name+'_x'+str(i+1) + """ PARTITION OF """+table_name+"""
            FOR VALUES FROM ("""+str(x_breaks[i]) +""") TO ("""+ str(x_breaks[i+1])+""")
	        PARTITION BY RANGE (""" + y_partition + """);
            """
        ##print(qurry)
        curs.execute(qurry)

        for j in range(len(y_breaks)-1):
            qurry = """\
            create table """ + table_name+'_x'+str(i+1)+'_y'+str(j+1) + """ PARTITION OF """+table_name+'_x'+str(i+1)+"""
            FOR VALUES FROM ("""+str(y_breaks[j]) +""") TO ("""+ str(y_breaks[j+1])+""")

            """
            curs.execute(qurry)
       
            bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
            bb_2_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))

            # Right neighbor (i, j) -> (i, j+1)
            if j < y_cells-1:
                bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
                bb_2_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+2))

            # Bottom neighbor (i, j) -> (i+1, j)
            if i < x_cells-1:
                bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
                bb_2_list.append(table_name+'_x'+str(i+2)+'_y'+str(j+1))

            # Bottom-right diagonal neighbor (i, j) -> (i+1, j+1)
            if i < x_cells-1 and j < y_cells-1:
                bb_1_list.append(table_name+'_x'+str(i+1)+'_y'+str(j+1))
                bb_2_list.append(table_name+'_x'+str(i+2)+'_y'+str(j+2))

    conn.commit()
    curs.close()
    conn.close()

    return bb_1_list, bb_2_list

def create_filltered_hda_table(source_table, head, tail, buffer_size, esp, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', cells = [], bbox = [], bbox_grid = [], time_max=None, d_gap_h = '500'):
    """
    Creates and stores Human Disturbance Areas (HDAs) for human trajectory pairs.

    This function should be called after `find_comparable_routes`. It creates and populates
    a table in the specified SQL database containing Human Disturbance Areas (HDAs) derived
    from pairs of points in human trajectories that may be part of an encounter event.

    These HDAs are used in later analyses to evaluate possible overlap or proximity between
    animal and human trajectories.

    Parameters
    ----------
    source_table : str
        Name of the table containing candidate encounter events, typically created by 
        `find_comparable_routes`.

    head : str, optional
        Optional prefix to add to the output table name (useful for testing or versioning).

    tail : str, optional
        Optional suffix to add to the output table name.

    db : str
        Path or name of the SQL database to update.

    buffer_size : int
        The radius of the HDAs to create. This should represent the distance at which a human 
        is likely to disturb the target animal based on study conditions.

    esp : float
        The distance parameter used by the Douglas–Peucker algorithm for trajectory simplification.

    time_max : float or int
        Preferred sampling frequency. Points from the original track will be re-added after the 
        Douglas–Peucker algorithm wherever the sampling interval exceeds this value. No points 
        will be interpolated; if no possible points can be added, the time gap is left unchanged.

    d_gap_h : int
        Maximum allowed distance between consecutive points in a human trajectory. Trajectory segments 
        exceeding this threshold will be excluded from HDA generation.

    Returns
    -------
    None
        This function does not return a Python object. It creates a new SQL table
        in the specified database containing the generated HDAs.

    The created table includes the following columns:

        - id_point             : INTEGER
        - temps                : TIME WITHOUT TIME ZONE
        - geom                 : GEOMETRY
        - id_sub_traj          : INTEGER
        - id_traj              : INTEGER
        - date                 : DATE
        - next_id_point        : INTEGER
        - next_temps           : TIME WITHOUT TIME ZONE
        - next_geom            : GEOMETRY
        - next_id_sub_traj     : INTEGER
        - next_id_traj         : INTEGER
        - HDA                  : GEOMETRY
        - x_grid               : INTEGER
        - y_grid               : INTEGER
        - x_coord              : DOUBLE PRECISION
        - y_coord              : DOUBLE PRECISION
    """

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\

    SELECT 
        '1',
        ti.id_traj_2 AS id_traj,
        st_x(p.geom),
        st_y(p.geom),
        st_z(p.geom),
        p.temps,
        p.*,
        FLOOR((st_x(p.geom) - 942749.5) / 25) as x_grid,
        FLOOR((st_y(p.geom) - 6504411.5) / 25) as y_grid,
        ti.date_2
    FROM (select distinct id_traj_2, date_2 from """+source_table+""")  ti
    LEFT JOIN sub_trajectories st ON st.id_traj = ti.id_traj_2
    LEFT JOIN points p ON p.id_sub_traj = st.id_sub_traj
    WHERE p.geom IS NOT NULL
    and extract(year from p.temps) != 1970
    and extract(year from p.temps) != 1971
    and temps is not null
    and st_x(p.geom) >	"""+ str(bbox[0]) +"""
    and st_x(p.geom) <	"""+ str(bbox[1]) +"""
    and st_y(p.geom) >	"""+ str(bbox[2]) +"""
    and st_y(p.geom) <	"""+ str(bbox[3]) +"""
    order by id_traj, temps, id_point;"""

    curs.execute(qurry)
    #print('Querry compleated')
    r = curs.fetchall()
    #print('Querry data saved in variable')

    af_list = ['id_point',
            'id_sub_traj',
            'geom',
            'temps',
            'outlier',
            'grid_x',
            'grid_y',
            'date_2']
    #print('af_list created')

    tracks = add_traces_from_lists(r,af_list)
    #print('Data placed in track collection')
    #print('Prefiltered num of traj ' + str(len(tracks)))

    #simplify
    for trace__ in tracks:
        trace__.cleanDuplicates("XY")
    #print('Duplicates deleated num of traj ' + str(len(tracks)))

    id_traj = []
    
    tracks_simp = track_collection.TrackCollection()
    
    #print('Starting simplicifation')
    for trace in tracks:

        trace_simp = simplify(trace, esp, time_max=time_max)
        tracks_simp.addTrack(trace_simp)

        id_traj.extend([trace.tid]*len(trace_simp))
        
    #print('Simplification finished')
    #print('Number of traj after filtering : ' + str(len(tracks_simp)))

    #create da table
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()
    
    qurry = 'DROP TABLE IF EXISTS ' + head + 'hda' + tail+ ';'
    curs.execute(qurry)
    conn.commit()
    #print('Dropped table if exists')

    variables = """\
        id_point 	        integer, \n
        temps               time without time zone,\n
        geom                geometry,\n
        id_sub_traj         integer, \n
        id_traj             integer, \n
        date                date,\n
        next_id_point       integer, \n
        next_temps          time without time zone,\n
        next_geom           geometry,\n
        next_id_sub_traj    integer, \n
        next_id_traj        integer, \n
        x_grid              integer,\n
        y_grid              integer,\n
        next_x_grid         integer,\n
        next_y_grid         integer,\n
        x_coord				double precision,
        y_coord 			double precision,
        geom_line           geometry,
        hda                  geometry  
        """

    table_name =  head + 'hda' + tail

    if not cells:
        ##print('here 8')

        qurry = """\
                create table """ + table_name + """ (
                """+ variables +"""
                );
                """
        
        curs.execute(qurry)
        conn.commit()
    elif cells:

        ##print('here 8a')

        _,bb_2_list_hda = table_partitioning(table_name, 
                   variables, 
                   'x_grid', 
                   'y_grid', 
                   bbox_grid, 
                   cells, 
                   cells,
                   db)
    
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)
    #print('Event table created')

    curs = conn.cursor()

    d  = list(zip(
        tracks_simp.getAnalyticalFeature('id_point')[0:-1],  # Pull the first 10 data points
        tracks_simp.getTimestamps_str()[0:-1],  # Pull the first 10 data points
        tracks_simp.getAnalyticalFeature('geom')[0:-1],  # Pull the first 10 data points
        tracks_simp.getAnalyticalFeature('id_sub_traj')[0:-1],  # Pull the first 10 data points
        id_traj[0:-1],  # Pull the first 10 data points
        tracks_simp.getAnalyticalFeature('date_2')[0:-1],  # Pull the first 10 data points

        tracks_simp.getAnalyticalFeature('id_point')[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getTimestamps_str()[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('geom')[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('id_sub_traj')[1:],  # Pull the next 10 data points (shifted by 1)
        id_traj[1:],  # Pull the next 10 data points (shifted by 1)

        tracks_simp.getAnalyticalFeature('grid_x')[0:-1],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('grid_y')[0:-1],
        tracks_simp.getAnalyticalFeature('grid_x')[1:],  # Pull the next 10 data points (shifted by 1)
        tracks_simp.getAnalyticalFeature('grid_y')[1:]   # Pull the next 10 data points (shifted by 1)
    ))

    #print('Data prepared')

    curs.executemany("""
            insert into """ + head + """hda""" + tail+ """(
                id_point, 
                temps, 
                geom, 
                id_sub_traj, 
                id_traj,
                date,
                next_id_point,
                next_temps,
                next_geom,
                next_id_sub_traj,
                next_id_traj,
                x_grid,
                y_grid,
                next_x_grid,
                next_y_grid
            )
                VALUES( %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s                   
                        )
                """,d)

    conn.commit()
    curs.close()
    conn.close()
    #print('HDA table created')

    #populate da table
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    #print('Filtering HDA table')

    qurry = """\

    delete from """ + head + """hda""" + tail+ """
    where id_traj != next_id_traj;

    delete from """ + head + """hda""" + tail+ """
    where id_point = next_id_point;

    delete from """ + head + """hda""" + tail+ """
    where next_id_traj is null;

    update """ + head + """hda""" + tail+ """ 
    set geom_line = st_makeline(geom,next_geom);

    delete from """ + head + """hda""" + tail+ """
    where st_length(geom_line) >= """ + str(d_gap_h) + """;

    update """ + head + """hda""" + tail+ """ 
    set hda = ST_Simplify(st_buffer(ST_SetSRID(geom_line, 2154),""" + str(buffer_size)+ """),1);
      
    """


    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()
    #print('Finished')

    return tracks, tracks_simp, id_traj

def simplify(track, tolerance, verbose=True, time_max = None):
     """
     Generic method to simplify a track. The process "Track simplification" 
     generally returns a new simplified track. Tolerance is in the unit 
     of track observation coordinates.
     
     Differents modes of simplification are implemented in tracklib:
          
     - MODE_SIMPLIFY_DOUGLAS_PEUCKER (1)
               tolerance is max allowed deviation with respect to straight line
     - MODE_SIMPLIFY_VISVALINGAM (2)
               tolerance is maximal triangle area of 3 consecutive points
     - MODE_SIMPLIFY_SQUARING (3)
               tolerance is threshold on flat and right angles
     - MODE_SIMPLIFY_MINIMIZE_LARGEST_DEVIATION (4)
               tolerance is typical max deviation with respect to straight line
     - MODE_SIMPLIFY_MINIMIZE_ELONGATION_RATIO (5)
               tolerance is typical elongation ratio of min bounding rectangle
     - MODE_SIMPLIFY_PRECLUDE_LARGE_DEVIATION (6)
               tolerance is max allowed deviation with respect to straight line
     - MODE_SIMPLIFY_FREE (7)
               tolerance is a customed function to minimize
     - MODE_SIMPLIFY_FREE_MAXIMIZE (8)
               tolerance is a customed function to maximize

     """
     if time_max is None:
          return douglas_peucker(track, tolerance)
     else:
          track_simp = douglas_peucker(track, tolerance)
          return read_time(track, track_simp, time_max)
    
def douglas_peucker (track, eps):
    """
    Function to simplify a GPS track with Douglas-Peucker algorithm.

    The Douglas-Peucker algorithm reduce the number of a line by reducing
    the number of points. The result should keep the original shape.

    Parameters
    ----------
    :param track Track: GPS track
    :param eps float: length threshold epsilon (sqrt of triangle area)
    :return Track: simplified track

    """

    L = track.getObsList()
    
    temp_lists = {}
    if len(track.getListAnalyticalFeatures()) > 0:
        AF_list = track.getListAnalyticalFeatures()
        for list_name in (AF_list):
            temp_lists[list_name] = track.getAnalyticalFeature(list_name)  # Assign values to each list
   

    n = len(L)
    if n <= 2:
        track_sp = tk.Track(L)
        if len(track.getListAnalyticalFeatures()) > 0:
            for af in AF_list:
                track_sp.createAnalyticalFeature(af, temp_lists[list_name])
        return track_sp

    dmax = 0
    imax = 0

    for i in range(0, n):
        x0 = L[i].position.getX()
        y0 = L[i].position.getY()
        xa = L[0].position.getX()
        ya = L[0].position.getY()
        xb = L[n - 1].position.getX()
        yb = L[n - 1].position.getY()
        d = distance_to_segment(x0, y0, xa, ya, xb, yb)
        if d > dmax:
            dmax = d
            imax = i

    if dmax < eps:
        track_sp = tk.Track([L[0], L[n - 1]], user_id=track.uid, track_id=track.tid, base=track.base)
        if len(track.getListAnalyticalFeatures()) > 0:
            for af in AF_list:
                track_sp.createAnalyticalFeature(af, temp_lists[list_name][0:n-1])
        return track_sp
    else:
        XY1 = tk.Track(L[0:imax], user_id=track.uid, track_id=track.tid, base=track.base)
        XY2 = tk.Track(L[imax:n], user_id=track.uid, track_id=track.tid, base=track.base)
        if len(track.getListAnalyticalFeatures()) > 0:
            for af in AF_list:
                XY1.createAnalyticalFeature(af, temp_lists[list_name][0:imax])
                XY2.createAnalyticalFeature(af, temp_lists[list_name][imax:n])

        return douglas_peucker(XY1, eps) + douglas_peucker(XY2, eps)
    
def distance_to_segment(x0: float, y0: float, x1: float, y1: float, x2: float, y2: float) -> float:   
    """Function to compute distance between a point and a segment

    :param x0: point coordinate X
    :param y0: point coordinate Y
    :param x1: segment first point X
    :param y1: segment first point Y
    :param x2: segment second point X
    :param y2: segment second point Y

    :return: Distance between point and projection coordinates
    """

    # Segment length
    l = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))+0.00000000000000000000000000000000000000001

    # Normalized scalar product
    psn = ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / l

    X = max(x1, x2)
    Y = max(y1, y2)

    x = min(x1, x2)
    y = min(y1, y2)

    xproj = x1 + psn / l * (x2 - x1)
    yproj = y1 + psn / l * (y2 - y1)

    xproj = min(max(xproj, x), X)
    yproj = min(max(yproj, y), Y)

    # Compute distance
    d = math.sqrt((x0 - xproj) * (x0 - xproj) + (y0 - yproj) * (y0 - yproj))

    return d

def read_time(track, track_simp, time_max):
    j = 0  # Initialize j for tracking position in the track list
    i = 0  # Initialize i for tracking position in the track_simp list
    
    while i < len(track_simp) - 1:  # Ensure i doesn't exceed the second-to-last element of track_simp
        ##print(f"Checking i = {i}, timestamp = {track_simp.getObs(i).timestamp}")
        
        # Check if the time gap between consecutive observations in track_simp exceeds the max time threshold
        if track_simp.getObs(i + 1).timestamp - track_simp.getObs(i).timestamp > time_max:
            # Ensure j is at least i (moving j forward if needed)
            if j < i:
                j = i
            
            # Move j to the correct position in track where the timestamp is just before the one in track_simp
            while j < len(track) and track.getObs(j).timestamp <= track_simp.getObs(i).timestamp:
                ##print('Moving j to position before track_simp[i]')
                j += 1
            if track.getObs(j).timestamp == track_simp.getObs(i + 1).timestamp:
                ##print('there are no inbetween time steps')
                i+=1
                continue
            while j < len(track) and track.getObs(j).timestamp < track_simp.getObs(i + 1).timestamp and track.getObs(j).timestamp-track_simp.getObs(i).timestamp < time_max:
                j +=1
            if  track.getObs(j-1).timestamp > track_simp.getObs(i).timestamp:
                    track_simp.insertObs(track.getObs(j), i + 1)
            elif track.getObs(j-1).timestamp == track_simp.getObs(i).timestamp:
                    track_simp.insertObs(track.getObs(j), i + 1)
            else:
                #print('Sothing BAD')
                break
        i += 1

    return track_simp

def add_traces_from_lists(LINES, AF_list):


    tracks = track_collection.TrackCollection()
    time_fmt_save = ObsTime.getReadFormat()
    ObsTime.setReadFormat('4Y-2M-2DT2h:2m:2sZ')

    if len(AF_list) != len(LINES[0])- 6:
        raise WrongArgumentError("Error: AF_list : " + str(len(AF_list)) + " does not match extra data " + str(len(LINES[0])- 6))
    else:
        #print('Made it to make AF')
        temp_lists = {}
        # Dynamically create lists based on the list_names and values
        for list_name in (AF_list):
            temp_lists[list_name] = []  # Assign values to each list
    
    trace = tk.Track([],1)
    trace.no_data_value = -99999
    trace.uid = LINES[0][0]
    trace.tid = LINES[0][1]

    #print('created the first trace : ' + str(trace.tid))
    for row in LINES:
        
        id_user = row[0]
        id_traj = row[1]
        EE = row[2]
        NN = row[3]
        UU = row[4]
        TT  = row[5]
        sridd = "ENU"
        #if not row[6] or row[6] == '2154':
        #    sridd = 'ENU'
               
        if id_user != trace.uid or id_traj != trace.tid:
            if trace is None:
                continue
            if trace.size() <= 0:
                continue
            for af in AF_list:
                trace.createAnalyticalFeature(af, temp_lists[af])
                temp_lists[af] = []
            ##print(type(trace))
            tracks.addTrack(trace)
            trace = tk.Track([],1)
            trace.no_data_value = -99999
            trace.uid = id_user
            trace.tid = id_traj


        if id_user == trace.uid and id_traj == trace.tid:
            if TT: 
                time = ObsTime.readTimestamp(str(TT))
            else:
                time = ObsTime()

            if EE == None:
                E = trace.no_data_value
            else:
                try:
                    E = (float)(EE)
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float ()")

            if NN == None:
                N = trace.no_data_value
            else:
                try:
                    N = (float)(NN)
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float ()")

            if UU == None:
                U = trace.no_data_value
            else:
                try:
                    U = (float)(UU)
                except:
                    raise WrongArgumentError("Parameter E or N is not an instantiation of a float ()")


            if (int(E) != trace.no_data_value) and (int(N) != trace.no_data_value):
                if not sridd in [
                    "ENUCOORDS", "ENU", "GEOCOORDS", "GEO", "ECEFCOORDS", "ECEF",
                ]:
                    raise WrongArgumentError("Error: unknown coordinate type [" + str(sridd) + "]")
                if sridd in ["ENUCOORDS", "ENU"]:
                    point = Obs(ENUCoords(E, N, U), time)
                #if sridd in ["GEOCOORDS", "GEO"]:
                #    point = Obs(GeoCoords(E, N, U), time)
                #if sridd in ["ECEFCOORDS", "ECEF"]:
                #    point = Obs(ECEFCoords(E, N, U), time)
                trace.addObs(point)

            else:
                no_data = trace.no_data_value
                trace.addObs(Obs(makeCoords(no_data, no_data, no_data, sridd), time))

            for i, af in enumerate(AF_list):
                temp_lists[af].append(row[i+6])
    if trace is not None and trace.size() > 0:
        for af in AF_list:
            trace.createAnalyticalFeature(af, temp_lists[af])
        tracks.addTrack(trace)

    return tracks

def create_encounter_events(source_ppa, source_hda, source_pairings, head, tail, comp_type, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', search_hda=None, search_ppa=None):
    """
    Compares animal Potential Path Areas (PPA) to human Disturbance Areas (HDA) for temporally close trajectories.

    This function analyzes spatial overlaps between animal PPAs and human disturbance areas for trajectory pairs
    that are sufficiently close in time, based on a specified temporal shift. It should be called after
    the PPA and HDA tables have been created.

    Parameters
    ----------
    source_ppa : str
        Name of the table containing animal Potential Path Areas.

    source_hda : str
        Name of the table containing human Disturbance Areas.

    source_pairings : str
        Name of the table containing trajectory pairings.

    head : str
        Prefix to add to the output table name (useful for testing or distinguishing tables).

    tail : str
        Suffix to add to the output table name (useful for testing or distinguishing tables).

    comp_type : str
        Type of comparison or method used for encounter event detection.

    db : str
        Name or path of the SQL database where the encounter events table will be created and updated.

    search_hda : list, optional
        List of specific human disturbance area identifiers or filters to limit the search (default is None).

    search_ppa : list, optional
        List of specific potential path area identifiers or filters to limit the search (default is None).

    Returns
    -------
    None
        This function does not return a value.
        It creates and populates a table containing encounter events, representing potential small segments of an encounter.
    """




    if comp_type.lower() == 'grid':
        search_by = """\
                            abs(a_.x_grid-b_.x_grid) <= 35
                        and abs(a_.y_grid-b_.y_grid) <= 35
                        and a_.temps <= b_.next_temps 
                        and	b_.temps <= a_.next_temps
                        and	st_intersects(a_.ppa, b_.hda)
                    """
    elif comp_type.lower() == 'geom':
        search_by = """\
                            st_intersects(a_.ppa, b_.hda)
                        and a_.temps <= b_.next_temps 
                        and	b_.temps <= a_.next_temps
                    """
    else:
        print('Search type not implamented')

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
        DROP TABLE IF EXISTS """ + head + """encounter_event""" + tail+ """;
        CREATE TABLE """ + head + """encounter_event""" + tail+ """(
            id_encounter_event SERIAL PRIMARY KEY,
            id_traj integer,
            id_sub_traj integer,
                id_point integer,
                geom geometry,
                temps time without time zone,
            
                next_id_point integer,
                next_geom geometry,
                next_temps time without time zone,
            
                geom_line geometry,
                ppa geometry,
            
            id_traj_2 integer,
            id_sub_traj_2 integer,
                id_point_2 integer,
                geom_2 geometry,
                temps_2 time without time zone,
            
                next_id_point_2 integer,
                next_geom_2 geometry,
                next_temps_2 time without time zone,
            
                geom_line_2 geometry,
                hda geometry,
            shortest_length numeric
        );
    """

    curs.execute(qurry)


    conn.commit()
    curs.close()
    conn.close()


    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
        --Finds and saves overlaps
        insert into """ + head + """encounter_event""" + tail+ """(
            id_traj,
            id_sub_traj,
                id_point ,
                geom ,
                temps ,
            
                next_id_point ,
                next_geom ,
                next_temps ,
                
                geom_line,
                -- ppa ,
            
            id_traj_2 ,
            id_sub_traj_2,
                id_point_2 ,
                geom_2 ,
                temps_2 ,
            
                next_id_point_2 ,
                next_geom_2 ,
                next_temps_2 ,
            
                geom_line_2 ,
                -- hda,
                shortest_length
                )
                
        select 
            a_.id_traj ,
            a_.id_sub_traj,
                a_.id_point ,
                a_.geom ,
                a_.temps ,
            
                a_.next_id_point ,
                a_.next_geom ,
                a_.next_temps ,
            
                a_.geom_line,
                -- a_.ppa ,
            
            b_.id_traj ,
            b_.id_sub_traj,
                b_.id_point ,
                b_.geom ,
                b_.temps ,
            
                b_.next_id_point ,
                b_.next_geom ,
                b_.next_temps ,
            
                b_.geom_line ,
                -- b_.hda,
            ST_Distance(a_.geom_line, b_.geom_line)
        FROM """ + source_ppa + """ AS a_
        inner join """ + source_pairings + """ as c_
            on c_.id_traj_1 = a_.id_traj
        INNER JOIN """ + source_hda + """ AS b_
            on c_.id_traj_2 = b_.id_traj
        where""" + search_by 

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()
    return qurry

def assign_encounters(source_table, threshold, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', id_column = None, vis_column = 'vis_grid'):
    """
    Assigns encounter IDs to consecutive encounter events based on specified criteria.

    This function groups consecutive encounter events that meet defined temporal criteria 
    into the same encounter by assigning matching encounter IDs. It updates the source table 
    with these assigned IDs.

    It should be called after visibility processing in QGIS (either within the QGIS application 
    or via Python integration) and before creating encounter summary tables.

    Parameters
    ----------
    source_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    threshold : float
        Maximum allowed time gap between two encounter events for them to be considered part 
        of the same encounter.

    db : str
        Name or path of the SQL database containing the encounter events table to be updated.

    Returns
    -------
    None
        This function does not return a value.
        It updates the encounter events table in the linked database by assigning encounter IDs.
    """


    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    save_print = ObsTime.getPrintFormat()
    ObsTime.setPrintFormat("4Y-2M-2D 2h:2m:2s")
    
    qurry = """\

        SELECT 
            id_encounter_event,

            id_traj,
            id_traj_2,
            id_sub_traj,
            id_sub_traj_2,

            geom,
            next_geom,
            geom_2,
            next_geom_2,

            temps_2,
            next_temps_2

        -- date(temps)     as date_human,
        -- date(temps_2)   as date_animal

        FROM """ + source_table +"""
            -- and time_h is not null
            -- and abs(extract(doy from time_h)-extract(doy from temps)) <= 15
            -- and date(time_h) != '1970-00-00'
        where """+vis_column+""" = true

        order by 
            id_traj,
            id_traj_2, 
            temps_2
        """
    curs.execute(qurry)

    #print("Data Querryed")

    id_encounter_event=[]

    id_traj=[]
    id_traj_2=[]
    id_sub_traj=[]
    id_sub_traj_2=[]

    geom=[]
    next_geom=[]
    geom_2=[]
    next_geom_2=[]

    temps_2=[]
    next_temps_2=[]

    date_human=[]
    date_animal=[]

    trace  = tk.Track([],1)

    for row in curs.fetchall():

        id_encounter_event.append(row[0])

        id_traj.append(row[1])
        id_traj_2.append(row[2])
        id_sub_traj.append(row[3])
        id_sub_traj_2.append(row[4])

        geom.append(row[5])
        next_geom.append(row[6])
        geom_2.append(row[7])
        next_geom_2.append(row[8])

        temps_2.append(row[9])
        next_temps_2.append(row[10])

        #date_human.append(row[11])
        #date_animal.append(row[12])

        trace.addObs(Obs(ENUCoords(row[4],row[5],-1),ObsTime.readTimestamp('1970-01-01 '+str(row[9]))))
            
    trace.createAnalyticalFeature('id_encounter_event', id_encounter_event)
    trace.createAnalyticalFeature('id_traj', id_traj)
    trace.createAnalyticalFeature('id_traj_2', id_traj_2)
    #trace.createAnalyticalFeature('date_h', date_human)
    #trace.createAnalyticalFeature('date_a', date_animal)

    trace.addAnalyticalFeature(make_trace_segment(threshold))
    segmentation(trace, ["trace_segment"],"out",[0.5],"and")
    tracks = split(trace, "out")
    
    for j in range(len(tracks)):
        id_encounter_create(tracks,j)

    d = list(zip(tracks.getAnalyticalFeature('id_encounter_event'),tracks.getAnalyticalFeature('id_encounter')))

    psycopg2.extensions.register_adapter(float, nan_to_null)
    psycopg2.extensions.register_adapter(np.bool_, bool_to_bool)

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    if not id_column:
        id_column = 'id_encounter'
    

    curs.execute("""
    alter table """ + source_table + """
    add """ + id_column + """ integer""")

    curs.executemany("""
    update """ + source_table + """
    set id_encounter = %s
    where id_encounter_event = %s
    """,(list(zip(tracks.getAnalyticalFeature('id_encounter'),
        tracks.getAnalyticalFeature('id_encounter_event')))))

    conn.commit()
    curs.close()
    conn.close()
    
    ObsTime.setPrintFormat(save_print)

def assign_encounters_SQL(source_table, threshold, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', id_column = 'id_encounter', vis_column = 'vis_grid'):
    """
    Assigns encounter IDs to consecutive encounter events based on specified criteria.

    This function groups consecutive encounter events that meet defined temporal criteria 
    into the same encounter by assigning matching encounter IDs. It updates the source table 
    with these assigned IDs.

    It should be called after visibility processing in QGIS (either within the QGIS application 
    or via Python integration) and before creating encounter summary tables.

    Parameters
    ----------
    source_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    threshold : float
        Maximum allowed time gap between two encounter events for them to be considered part 
        of the same encounter.

    db : str
        Name or path of the SQL database containing the encounter events table to be updated.

    Returns
    -------
    None
        This function does not return a value.
        It updates the encounter events table in the linked database by assigning encounter IDs.
    """
    
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
    
    ALTER TABLE """+str(source_table)+""" 
    ADD COLUMN """+str(id_column)+""" INT;

    WITH ordered AS (
    SELECT
        *,
		temps_2 as start_time,
		next_temps_2 as end_time,
        lag(id_traj)   OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event) AS prev_id_traj,
        lag(id_traj_2) OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event) AS prev_id_traj_2,
        lag(next_temps_2)   OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event) AS prev_end_time
    FROM """+str(source_table)+"""

    where """+vis_column+""" = TRUE

    ),
    flagged AS (
    SELECT *,
        CASE
        WHEN prev_id_traj   IS DISTINCT FROM id_traj   THEN 1
        WHEN prev_id_traj_2 IS DISTINCT FROM id_traj_2 THEN 1
        WHEN EXTRACT(EPOCH FROM (start_time - prev_end_time)) > """+str(threshold)+""" THEN 1
        ELSE 0
        END AS is_new_encounter
    FROM ordered
    ),
    numbered AS (
    SELECT *,
        SUM(is_new_encounter) OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event ROWS UNBOUNDED PRECEDING) AS new_id_encounter
    FROM flagged
    )
    UPDATE """+str(source_table)+""" e
    SET """+str(id_column)+""" = n.new_id_encounter
    FROM numbered n
    WHERE e.id_encounter_event = n.id_encounter_event;
    """

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()

def assign_encounters_SQL_old(source_table, threshold, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', id_column = 'id_encounter', vis_column = 'vis_grid'):
    """
    Assigns encounter IDs to consecutive encounter events based on specified criteria.

    This function groups consecutive encounter events that meet defined temporal criteria 
    into the same encounter by assigning matching encounter IDs. It updates the source table 
    with these assigned IDs.

    It should be called after visibility processing in QGIS (either within the QGIS application 
    or via Python integration) and before creating encounter summary tables.

    Parameters
    ----------
    source_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    threshold : float
        Maximum allowed time gap between two encounter events for them to be considered part 
        of the same encounter.

    db : str
        Name or path of the SQL database containing the encounter events table to be updated.

    Returns
    -------
    None
        This function does not return a value.
        It updates the encounter events table in the linked database by assigning encounter IDs.
    """
    
    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    qurry = """\
    
    ALTER TABLE """+str(source_table)+""" 
    ADD COLUMN """+str(id_column)+""" INT;

    WITH ordered AS (
    SELECT
        *,
        lag(id_traj)   OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event) AS second_id_traj,
        lag(id_traj_2) OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event) AS second_id_traj_2,
        lag(temps_2)   OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event) AS second_temps_2
    FROM """+str(source_table)+"""

    where """+vis_column+""" = TRUE

    ),
    flagged AS (
    SELECT *,
        CASE
        WHEN second_id_traj   IS DISTINCT FROM id_traj   THEN 1
        WHEN second_id_traj_2 IS DISTINCT FROM id_traj_2 THEN 1
        WHEN EXTRACT(EPOCH FROM (second_temps_2 - next_temps_2)) > """+str(threshold)+""" THEN 1
        ELSE 0
        END AS is_new_encounter
    FROM ordered
    ),
    numbered AS (
    SELECT *,
        SUM(is_new_encounter) OVER (ORDER BY id_traj,id_traj_2, temps_2, id_encounter_event ROWS UNBOUNDED PRECEDING) AS new_id_encounter
    FROM flagged
    )
    UPDATE """+str(source_table)+""" e
    SET """+str(id_column)+""" = n.new_id_encounter
    FROM numbered n
    WHERE e.id_encounter_event = n.id_encounter_event;
    """

    curs.execute(qurry)

    conn.commit()
    curs.close()
    conn.close()
    
def make_trace_segment(threshold_seconds):
    def trace_segment (track, i):
        id_i = track.getObsAnalyticalFeature('id_traj',i)
        id_2 = track.getObsAnalyticalFeature('id_traj',i+1)
        
        name_i = track.getObsAnalyticalFeature('id_traj_2',i)
        name_2 = track.getObsAnalyticalFeature('id_traj_2',i+1)

        time_gap = track.getT(i+1) - track.getT(i)
        
        if id_i != id_2 or name_i != name_2 or time_gap > threshold_seconds:
            return 1
        else:
            return 0
    return trace_segment

def id_encounter_create(track,j):
    track[j].createAnalyticalFeature('id_encounter', j)

def nan_to_null(f,
        _NULL=psycopg2.extensions.AsIs('NULL'),
        _Float=psycopg2.extensions.Float):
    
    """
    Is used to convert nan valuses from python when uploading to SQL"""
    if not np.isnan(f):
        return _Float(f)
    return _NULL

def bool_to_bool(b,
        _NULL=psycopg2.extensions.AsIs('NULL'),
        _Bool=psycopg2.extensions.Boolean):
    if isinstance(b, np.bool_):
        return _Bool(b)
    return _NULL

def segmentation(track, afs_input, af_output, 
                 thresholds_max, mode_comparaison="and"):
    """
    Method to divide a track into multiple according to analytical feaures value.
    Creates an AF with 0 if change of division, 1 otherwise
    """

    # Gestion cas un seul AF
    if not isinstance(afs_input, list):
        afs_input = [afs_input]
    if not isinstance(thresholds_max, list):
        thresholds_max = [thresholds_max]

    track.createAnalyticalFeature(af_output)

    for i in range(track.size()):

        # On cumule les comparaisons pour chaque af_input
        if mode_comparaison == "and":
            comp = True
        else:
            comp = False

        for index, af_input in enumerate(afs_input):
            current_value = track.getObsAnalyticalFeature(af_input, i)

            # on compare uniquement si on peut
            if not isnan(current_value):

                seuil_max = sys.float_info.max
                if thresholds_max != None and len(thresholds_max) >= index:
                    seuil_max = thresholds_max[index]

                if mode_comparaison == "and":
                    comp = comp and (current_value <= seuil_max)
                else:
                    comp = comp or (current_value <= seuil_max)

        #  On clot l'intervalle, on le marque a 1
        if not comp:
            track.setObsAnalyticalFeature(af_output, i, 1)
        else:
            track.setObsAnalyticalFeature(af_output, i, 0)

def split(track, source, limit=0):
    """
    Splits track according to :
        - af name (considered as a marker) if `source` is a string
        - list of index if `source` is a list
        
    if limit > 0, only track which have more or equal than limit points are keeped.

    :return: No track if no segmentation, otherwise a TrackCollection object
    """

    NEW_TRACES = track_collection.TrackCollection()

    # --------------------------------------------
    # Split from analytical feature name
    # --------------------------------------------
    if isinstance(source, str):
        count = 0  # Initialisation du compteur des étapes
        begin = 0  # indice du premier point de l'étape
        for i in range(track.size()):
            # Nouvelle trajectoire
            if track.getObsAnalyticalFeature(source, i) == 1:  

                # L'identifiant de la trace subdivisée est obtenue par concaténation
                # de l'identifiant de la trace initiale et du compteur
                # Important pour les pauses
                new_id = str(track.uid) + "." + str(count) + "." + str(begin) + "." + str(i)

                # La liste de points correspondant à l'intervalle de subdivision est créée
                newtrack = track.extract(begin, i)
                begin = i + 1
                newtrack.setUid(new_id)

                if (limit > 0 and newtrack.length() < limit):
                    continue
        
                NEW_TRACES.addTrack(newtrack)
                count += 1

        # Si tous les points sont dans la même classe, la liste d'étapes reste vide
        # sinon, on clôt la derniere étape et on l'ajoute à la liste
        if begin != 0:
            # Formalisme Important pour les pauses
            new_id = str(track.uid) + "." + str(count)+ "." + str(begin) + "." + str(track.size()-1)
            newtrack = track.extract(begin, track.size() - 1)
            
            if limit == 0 or (limit > 0 and newtrack.length() >= limit):
                newtrack.setUid(new_id)
                NEW_TRACES.addTrack(newtrack)

    # --------------------------------------------
    # Split from list of indices
    # --------------------------------------------
    if isinstance(source, list):
        for i in range(len(source) - 1):
            newtrack = track.extract(source[i], source[i + 1])
            if (limit > 0 and newtrack.length() < limit):
                continue
            NEW_TRACES.addTrack(newtrack)

    # RETURN collection
    return NEW_TRACES

def isnan(number: Union[int, float]) -> bool:   
    """Called to """
    return number != number

def create_encounter_table_without_geom(source_table, traj_pair_tables, head, tail, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', id_column = 'id_encounter', vis_column = 'vis_grid'):
    """
    Creates and populates an encounter summary table in the specified SQL database.

    This function should be run after `assign_encounters` has completed. It generates a table 
    that summarizes encounter events between trajectories, using data from the source encounter 
    events and trajectory pair tables.

    Parameters
    ----------
    source_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    traj_pair_tables : str
        Name of the table containing trajectory pairs, typically created by `find_comparable_routes`.

    head : str
        Prefix to add to the encounter table name (useful for testing or distinguishing tables).

    tail : str
        Suffix to add to the encounter table name (useful for testing or distinguishing tables).

    db : str
        Name or path of the SQL database where the encounter table will be created and updated.

    Returns
    -------
    None
        This function does not return a value.
        It creates and populates an encounter table in the database with the following columns:

        - id_encounter (INTEGER PRIMARY KEY)
        - earliest_time (TIMESTAMP or DATETIME)
        - latest_time (TIMESTAMP or DATETIME)
        - date_animal (DATE)
        - date_human (DATE)
        - min_dist (NUMERIC)
        - vis (BOOLEAN)
    """

    #if not id_column:
    #    id_column = 'id_encounter'

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    curs.execute("""

        drop table if exists """+head+"""Encounter"""+tail+""";

        CREATE TABLE """+head+"""Encounter"""+tail+"""(
            id_encounter integer primary key,
            earliest time,
            latest time,
            date_animal date,
            date_human date,
            min_dist numeric,
            vis boolean
        );


        INSERT INTO """+head+"""Encounter"""+tail+""" (
            id_encounter,
            earliest,
            latest,
            date_animal,
            date_human,
            min_dist,
            vis
        )
        SELECT 
            a_."""+id_column+""", 
            MIN(a_.temps_2::time) AS earliest,  -- Renamed for clarity
            MAX(a_.next_temps_2::time) AS latest,  -- Renamed for clarity
            b_.date_1 as date_animal,
            b_.date_2 as date_human,
            MIN(a_.shortest_length) AS min_dist, -- MIN(ST_Length(ST_ShortestLine(ppa, geom_line_2))) AS min_dist,
            bool_or(a_."""+vis_column+""") as vis
        FROM 
            """+source_table+""" as a_
        join 	"""+traj_pair_tables+""" as b_
            on  b_.id_traj_1 = a_.id_traj 
            and b_.id_traj_2 = a_.id_traj_2 

        where a_."""+vis_column+""" is true

        GROUP BY 
            """+id_column+""",
            b_.date_1,
            b_.date_2;
        """
	)

    conn.commit()
    curs.close()
    conn.close()

def create_encounter_table(source_table, traj_pair_tables, head, tail, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres', ppa_table = None, id_column = 'id_encounter', vis_column = 'vis_grid', ECA_h_radius = 10):
    """
    Creates and populates an encounter summary table in the specified SQL database.

    This function should be run after `assign_encounters` has completed. It generates a table 
    that summarizes encounter events between trajectories, using data from the source encounter 
    events and trajectory pair tables.

    Parameters
    ----------
    source_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    traj_pair_tables : str
        Name of the table containing trajectory pairs, typically created by `find_comparable_routes`.

    head : str
        Prefix to add to the encounter table name (useful for testing or distinguishing tables).

    tail : str
        Suffix to add to the encounter table name (useful for testing or distinguishing tables).

    db : str
        Name or path of the SQL database where the encounter table will be created and updated.

    Returns
    -------
    None
        This function does not return a value.
        It creates and populates an encounter table in the database with the following columns:

        - id_encounter (INTEGER PRIMARY KEY)
        - earliest_time (TIMESTAMP or DATETIME)
        - latest_time (TIMESTAMP or DATETIME)
        - date_animal (DATE)
        - date_human (DATE)
        - min_dist (NUMERIC)
        - vis (BOOLEAN)
    """

    #if not id_column:
    #    id_column = 'id_encounter'

    if not ppa_table:
        ppa_table = head+'ppa'+tail

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    curs.execute("""

        drop table if exists """+head+"""Encounter"""+tail+""";

        CREATE TABLE """+head+"""Encounter"""+tail+"""(
            id_encounter integer primary key,
            earliest time,
            latest time,
            date_animal date,
            date_human date,
            min_dist numeric,
            vis boolean,
            ECA_a geometry,
            ECA_h geometry
        );

        INSERT INTO """+head+"""Encounter"""+tail+""" (
            id_encounter,
            earliest,
            latest,
            date_animal,
            date_human,
            min_dist,
            vis,
            ECA_a,
            ECA_h
        )
        SELECT 
            a_."""+id_column+""", 
            MIN(a_.temps_2::time) AS earliest,  -- Renamed for clarity
            MAX(a_.next_temps_2::time) AS latest,  -- Renamed for clarity
            b_.date_1 as date_animal,
            b_.date_2 as date_human,
            MIN(a_.shortest_length) AS min_dist, -- MIN(ST_Length(ST_ShortestLine(ppa, geom_line_2))) AS min_dist,
            bool_or(a_."""+vis_column+""") as vis,
            st_union(ppa_.ppa),
            st_union(st_buffer(a_.geom_line_2, """+str(ECA_h_radius) +"""))
        FROM 
            """+source_table+""" as a_
        join 	"""+traj_pair_tables+""" as b_
            on  b_.id_traj_1 = a_.id_traj 
            and b_.id_traj_2 = a_.id_traj_2
        inner join """+ ppa_table+""" as ppa_
            on ppa_.id_point = a_.id_point
        where a_."""+vis_column+""" is true
        GROUP BY 
            """+id_column+""",
            b_.date_1,
            b_.date_2;
        """
	)

    conn.commit()
    curs.close()
    conn.close()

def join_vis_to_encounter_events(encounter_event_table, table_vis_grid, db = 'ResRoute', db_user = 'postgres', db_password = 'postgres',  vis_column = 'vis_grid'):
    """
    Creates and populates an encounter summary table in the specified SQL database.

    This function should be run after `assign_encounters` has completed. It generates a table 
    that summarizes encounter events between trajectories, using data from the source encounter 
    events and trajectory pair tables.

    Parameters
    ----------
    encounter_event_table : str
        Name of the table containing encounter events, typically created by `create_encounter_events`.

    table_vis_grid : str
        Name of the table containing visibility information between grid cells, typically created by 'visibility.py` run in QGIS.

    db : str
        Name or path of the SQL database where the encounter table will be created and updated.

    Returns
    -------
    None
        This function does not return a value.
        It creates and populated the visibility colum on an encounter events table:

    """

    conn = psycopg2.connect(database= db , user=db_user, password = db_password)

    curs = conn.cursor()

    
    ll_x = 924987.5
    ll_y = 6500012.5
    query = """\
        DROP TABLE IF EXISTS ttt;

        CREATE TEMPORARY TABLE ttt AS
        (SELECT 
                id_encounter_event,
                id_point,
                geom,
                id_point_2,
                geom_2,
                floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
                floor((st_y(geom)-"""+ str(ll_y) +""")/25) as y_grid,
                floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
                floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2
            FROM """+ encounter_event_table +"""
            UNION ALL	
            SELECT 
                id_encounter_event, 
                next_id_point,
                next_geom,
                next_id_point_2,
                next_geom_2,
                floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
                floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
                floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
                floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2            
            FROM """+ encounter_event_table +""" 
            UNION ALL	
            SELECT 
                id_encounter_event,
                id_point,
                geom,
                next_id_point_2,
                next_geom_2,
                floor((st_x(geom)-"""+ str(ll_x) +""")/25) as x_grid, 
                floor((st_y(geom)-"""+ str(ll_y) +""")/25 )as y_grid,
                floor((st_x(next_geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
                floor((st_y(next_geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2 
            FROM """+ encounter_event_table +""" 
            UNION ALL	
            SELECT 
                id_encounter_event,
                next_id_point,
                next_geom,
                id_point_2,
                geom_2,
                floor((st_x(next_geom)-"""+ str(ll_x) +""")/25) as x_grid, 
                floor((st_y(next_geom)-"""+ str(ll_y) +""")/25) as y_grid,
                floor((st_x(geom_2)-"""+ str(ll_x) +""")/25) as x_grid_2, 
                floor((st_y(geom_2)-"""+ str(ll_y) +""")/25) as y_grid_2             
            FROM """+ encounter_event_table +""" 
            ORDER BY id_encounter_event, x_grid, y_grid
        );

                    
        drop table if exists temppp;
        CREATE TEMPORARY TABLE temppp (
            id_encounter_event INTEGER PRIMARY KEY,
            vis BOOLEAN);

        insert into temppp (id_encounter_event, vis)	
        select a_.id_encounter_event, bool_or(b_.vis)
        from ttt as a_
        left join """+table_vis_grid+""" as b_
            on			a_.x_grid	= b_.x_grid
            and 		a_.y_grid	= b_.y_grid
            and 		a_.x_grid_2	= b_.x_grid_2
            and 		a_.y_grid_2	= b_.y_grid_2
        group by id_encounter_event;

        alter table """+ encounter_event_table +"""
        DROP COLUMN IF EXISTS """+vis_column+""";
                            
        alter table """+ encounter_event_table +"""
        add """+vis_column+""" boolean;

        drop index if exists id_encounter_event_"""+ encounter_event_table +"""_index;
        CREATE INDEX id_encounter_event_"""+ encounter_event_table +"""_index 
        ON """+ encounter_event_table +"""(id_encounter_event);


        UPDATE """+ encounter_event_table +""" as a_
        SET """+vis_column+""" = (
        SELECT vis
        FROM temppp
        WHERE temppp.id_encounter_event = a_.id_encounter_event)"""

    curs.execute(query)

    conn.commit()
    curs.close()
    conn.close()
