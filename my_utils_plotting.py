# %%

from sqlalchemy import create_engine  , text
import geopandas as gpd

def querry_ppa_indiv(source_table_events, source_table_encounters, source_table_ppa, vis = None, source_table_traj = [], time ='all', time_style = 'DD2', season='all', r_p = 'all', group_by = 'traj_human, indiv_animal' , db=[]): 
    db_connection_url = "postgresql://postgres:postgres@localhost:5432/"+db
    con = create_engine(db_connection_url)
    
    if time_style == 'DD2':
        if time == 'all':
            time_dd = "-- place homder"
            time_ = ' -- place homder '
        else:
            time_dd = "and c_.dawn_dusk_pm_2_hours ILIKE '%%"  + time+"%%'"
            time_ = ' -- place homder '
    elif time_style == 'DD':
            time_dd = "and c_.dawn_dusk ILIKE '%%"  + time+"%%'"
            time_ = ' -- place homder '
    elif time_style == 'Old': 
        time_dd = time_ = ' -- place homder '
        if time == 'all':
            time_ =   """   min(b_.temps_2)    <=   '23:59:59'
                            and '00:00:00'     <=   max(b_.next_temps_2)"""
        elif time == 'morning':
            time_ =   """   min(b_.temps_2)    <=  '04:00:00'
                            and '09:00:00'     <=   max(b_.next_temps_2)"""
        elif time == 'noon':
            time_ =   """   min(b_.temps_2)    <=  '9:00:00'
                            and '16:00:00'     <=   max(b_.next_temps_2)""" 
        elif time == 'evening':
            time_ =   """   min(b_.temps_2)    <=  '16:00:00'
                            and '20:30:00'     <=   max(b_.next_temps_2)"""  
        elif time == 'night':
            time_ =   """   min(b_.temps_2)    <=  '20:30:00'
                            and '04:00:00'     <=   max(b_.next_temps_2)"""
            
    if season == 'all':
        season_ = '1,2,3,4,5,6,7,8,9,10,11,12'
    elif season == 'hiking':
        season_ = '7,8'
    elif season == 'hunting':
        season_ = '9,10,11'
    elif season == 'skiing':
        season_ = '1,2,3'
    elif season == 'spring':
        season_ = '3,4,5'
    elif season == 'summer':
        season_ = '6,7,8'
    elif season == 'fall':
        season_ = '9,10,11'
    elif season == 'winter':
        season_ = '11,1,2'        

    if r_p == 'all':
        r_p_str = ' '
    elif r_p == 'r':
        r_p_str = ' and c_.date_animal = c_.date_human'
    elif r_p == 'p':
        r_p_str = ' and c_.date_animal != c_.date_human'
    elif r_p == 'y':
        r_p_str = 'and extract(doy from c_.date_animal) = extract(doy from c_.date_human)'
    elif type(r_p) == int:
        r_p_str = 'and abs(extract(doy from c_.date_animal) - extract(doy from c_.date_human)) <= '+ str(r_p)
    else:
        print('unrecognized')

    if vis is True:
        vis_ = """\
            and b_.vis_grid is True"""
        vis__ = ' -- place homder '
    elif vis is False:
        vis_ = ' -- place homder '
        vis__ = """\
            and bool_or(b_.vis_grid) is False"""
    elif vis is None:
        vis_ = ' -- place homder '
        vis__ = ' -- place homder '
    else:
        print('Vis error')

    if vis__ == ' -- place homder ' and time_ == ' -- place homder ':
        having = ' -- place homder '
    else:
        having = 'having'
  
 
    ppas = """
    select  ST_Union(geom) as geom -- , traj_human, indiv_animal
    from     (select
                c_.id_encounter,
                min(b_.temps_2),
                max(b_.next_temps_2),
                min(b_.shortest_length) as min_dist,
                c_.date_animal,
                c_.date_human,
                b_.id_traj_2 as traj_human, -- this is added to minimize autocorrelation 
                t_.id_indiv as indiv_animal, -- this is added to minimize autocorrelation 
                ST_Union(a_.ppa) as geom,
                CASE
                    WHEN c_.date_animal = c_.date_human  THEN 'Real'
                    ELSE 'Potential'
                END AS r_p
            from 	"""+source_table_ppa+""" as a_
            inner join 	"""+source_table_events+""" as b_
                on	a_.id_point = b_.id_point
            inner join 	"""+source_table_encounters+""" as c_
                on	b_.id_encounter = c_.id_encounter
            inner join trajectories as t_
                on b_.id_traj = t_.id_traj

            where   extract(month from c_.date_animal) in  ("""+season_+""")     
            """+ time_dd +"""  
            """+ r_p_str +"""
            """+ vis_ +"""
            group by 	c_.id_encounter,
                        c_.date_animal,
                        c_.date_human,
                        b_.id_traj_2,   -- this is added as part of auto corrilation fight
                        t_.id_indiv  -- this is added as part of auto corrilation fight
            """+having +""" 
            """+ time_ + """  
            -- and st_area(ST_Union(a_.ppa)) <= 2000
            """ + vis__ + """
            )
    group by """+ group_by    

    
    ppa = gpd.GeoDataFrame.from_postgis(ppas, con)
    return ppa 

def querry_enc(source_table_events, source_table_encounters, vis_column = 'vis_grid', source_table_traj = [], time ='all', season='all', r_p = 'all',  db=[]): 
    db_connection_url = "postgresql://postgres:postgres@localhost:5432/"+db
    con = create_engine(db_connection_url)
    
    if time == 'all':
        lower = '00:00:00'
        higher = '23:59:59' 
    elif time == 'morning':
        lower  = '04:00:00'
        higher = '9:00:00'
    elif time == 'noon': 
        lower  = '9:00:00'
        higher = '16:00:00'
    elif time == 'evening': 
        lower  = '16:00:00'
        higher = '20:30:00'
    elif time == 'night': 
        lower  = '20:30:00'
        higher = '04:00:00'
    
    if season == 'all':
        season_ = '1,2,3,4,5,6,7,8,9,10,11,12'
    elif season == 'hiking':
        season_ = '7,8'
    elif season == 'hunting':
        season_ = '9,10,11'
    elif season == 'sking':
        season_ = '1,2,3'
    elif season == 'spring':
        season_ = '3,4,5'
    elif season == 'summer':
        season_ = '6,7,8'
    elif season == 'fall':
        season_ = '9,10,11'
    elif season == 'winter':
        season_ = '11,1,2'  


    if r_p == 'all':
        r_p_str = ' '
    elif r_p == 'r':
        r_p_str = ' and c_.date_animal = c_.date_human'
    elif r_p == 'p':
        r_p_str = ' and c_.date_animal != c_.date_human'
    elif r_p == 'y':
        r_p_str = 'and extract(doy from c_.date_animal) = extract(doy from c_.date_human)'
    elif type(r_p) == int:
        r_p_str = 'and abs(extract(doy from c_.date_animal) - extract(doy from c_.date_human)) <= '+ str(r_p)
    else:
        print('unrecognized')

    if vis is True:
        vis_ = """\
            and b_."""+vis_column+""" is True"""
        vis__ = ' -- place homder '
    elif vis is False:
        vis_ = ' -- place homder '
        vis__ = """\
            and bool_or(b_.vis_grid) is False"""
    elif vis is None:
        vis_ = ' -- place homder '
        vis__ = ' -- place homder '
    else:
        print('Vis error')
 
    ecs = """
    select
        c_.id_encounter,
        min(b_.temps_2),
        max(b_.next_temps_2),
        min(b_.shortest_length) as min_dist,
        c_.date_animal,
		c_.date_human,
        st_collect(b_.geom) as geom,
        CASE
            WHEN c_.date_animal = c_.date_human  THEN 'Real'
            ELSE 'Potential'
        END AS r_p
    from    """+source_table_events+""" as b_
    inner join 	"""+source_table_encounters+""" as c_
        on	b_.id_encounter = c_.id_encounter
    where   extract(month from c_.date_animal) in  ("""+season_+""")     
    """+ r_p_str +"""
    """+ vis_ +"""
    group by 	c_.id_encounter,
                c_.date_animal,
		        c_.date_human
    having 
    min(b_.temps_2) <= '"""+higher+"""'
    and     '"""+lower+"""' <= max(b_.next_temps_2)
    """ + vis__

    ecs = gpd.GeoDataFrame.from_postgis(ecs, con)
    return ecs

def querry_enc_fig_9(source_table_events, source_table_encounters, vis = True,  vis_column = 'vis_grid', id_column = 'id_encounter', source_table_traj = [], time ='all', season='all', r_p = 'all',  db=[]): 
    db_connection_url = "postgresql://postgres:postgres@localhost:5432/"+db
    con = create_engine(db_connection_url)
    
    if time == 'all':
        lower = '00:00:00'
        higher = '23:59:59' 
    elif time == 'morning':
        lower  = '04:00:00'
        higher = '9:00:00'
    elif time == 'noon': 
        lower  = '9:00:00'
        higher = '16:00:00'
    elif time == 'evening': 
        lower  = '16:00:00'
        higher = '20:30:00'
    elif time == 'night': 
        lower  = '20:30:00'
        higher = '04:00:00'
    
    if season == 'all':
        season_ = '1,2,3,4,5,6,7,8,9,10,11,12'
    elif season == 'hiking':
        season_ = '7,8'
    elif season == 'hunting':
        season_ = '9,10,11'
    elif season == 'sking':
        season_ = '1,2,3'
    elif season == 'spring':
        season_ = '3,4,5'
    elif season == 'summer':
        season_ = '6,7,8'
    elif season == 'fall':
        season_ = '9,10,11'
    elif season == 'winter':
        season_ = '11,1,2'  


    if r_p == 'all':
        r_p_str = ' '
    elif r_p == 'r':
        r_p_str = ' and c_.date_animal = c_.date_human'
    elif r_p == 'p':
        r_p_str = ' and c_.date_animal != c_.date_human'
    elif r_p == 'y':
        r_p_str = 'and extract(doy from c_.date_animal) = extract(doy from c_.date_human)'
    elif type(r_p) == int:
        r_p_str = 'and abs(extract(doy from c_.date_animal) - extract(doy from c_.date_human)) <= '+ str(r_p)
    else:
        print('unrecognized')

    if vis is True:
        vis_ = """\
            and b_."""+vis_column+""" is True"""
        vis__ = ' -- place homder '
    elif vis is False:
        vis_ = ' -- place homder '
        vis__ = """\
            and bool_or(b_."""+vis_column+""") is False"""
    elif vis is None:
        vis_ = ' -- place homder '
        vis__ = ' -- place homder '
    else:
        print('Vis error')
 
    ecs = """
    select
        c_.id_encounter,
        min(b_.temps_2),
        max(b_.next_temps_2),
        min(b_.shortest_length) as min_dist,
        c_.date_animal,
		c_.date_human,
        st_collect(b_.geom) as geom,
        CASE
            WHEN c_.date_animal = c_.date_human  THEN 'Real'
            ELSE 'Potential'
        END AS r_p
    from    """+source_table_events+""" as b_
    inner join 	"""+source_table_encounters+""" as c_
        on	b_.""" + id_column + """ = c_.id_encounter
    where   extract(month from c_.date_animal) in  ("""+season_+""")     
    """+ r_p_str +"""
    """+ vis_ +"""
    group by 	c_.id_encounter,
                c_.date_animal,
		        c_.date_human
    having 
    min(b_.temps_2) <= '"""+higher+"""'
    and     '"""+lower+"""' <= max(b_.next_temps_2)
    """ + vis__

    ecs = gpd.GeoDataFrame.from_postgis(ecs, con)
    return ecs
