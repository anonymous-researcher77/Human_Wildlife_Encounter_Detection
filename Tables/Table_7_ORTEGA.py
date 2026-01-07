# %%
import ortega as ot
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import os
import re

con = psycopg2.connect(database='ResRoute', user='postgres')

runs = [[0,1],[1,25],[25,50],[50,75]]

head = 'exp__'

# %%
"""select b_.id_traj, b_.id_traj_2, min(a_.min_dist)
from """+head+"""encounter_default as a_ 
left join 	(select 
				distinct on (id_encounter) 
				id_encounter, 
				id_traj, 
				id_traj_2
			from """+head+"""encounter_event_default) as b_
	on a_.id_encounter = b_.id_encounter
group by b_.id_traj, b_.id_traj_2
having min(a_.min_dist) < 1
and min(a_.min_dist) >= 0
"""
def tfo(id_traj_1,id_traj_2, con):

    qurry = """\
    select 
        points.id_point, 
        trajectories.id_traj, 
        ST_X(ST_Transform(points.geom,4326)) as lon,
        ST_y(ST_Transform(points.geom,4326)) as lat,
        DATE '1970-01-01' + (points.temps - DATE_TRUNC('day', points.temps)) AS  temps  
    from trajectories
    inner join sub_trajectories
        on sub_trajectories.id_traj = trajectories.id_traj
    inner join points
        on points.id_sub_traj = sub_trajectories.id_sub_traj
    where trajectories.id_traj = """+str(id_traj_1)+""" and points.geom is not null and points.temps is not null
    or trajectories.id_traj = """+str(id_traj_2)+""" and points.geom is not null and points.temps is not null
    order by trajectories.id_traj, points.temps

    """
    dat = sqlio.read_sql_query(qurry, con)

    #con = None

    interactio = ot.ORTEGA(data=dat,
                        minute_max_delay=5,
                        latitude_field='lat',
                        longitude_field='lon',
                        time_field='temps',
                        id_field='id_traj')

    interactio.compute_ppa_perimeter()
    interactio.compute_ppa_interval()
    interactio.compute_ppa_area()
    interactio.compute_ppa_speed()

    interactio.compute_ppa_perimeter()
    os.system('cls')

    res = interactio.interaction_analysis()

    if res == None:
        return 0
    else:
        interactions = res.df_interaction_events

        return len(interactions)
    
def tfo_with_filtering(id_traj_1,id_traj_2, con):

    qurry = """\
    
        SELECT 
                ani_points.id_point, 
                ani_points.id_traj,
                ani_points.geom,
                ST_X(ST_Transform(ani_points.geom,4326)) AS lon,
                ST_Y(ST_Transform(ani_points.geom,4326)) AS lat,
                DATE '1970-01-01' + (ani_points.temps - DATE_TRUNC('day', ani_points.temps)) AS temps

        FROM """+head+"""ppa_default AS ani_points
        WHERE ani_points.id_traj = """+str(id_traj_1)+"""
        AND ani_points.geom IS NOT NULL 
        AND ani_points.temps IS NOT NULL

        UNION

        SELECT 
                ani_points.next_id_point, 
                ani_points.next_id_traj,
                ani_points.next_geom,
                ST_X(ST_Transform(ani_points.next_geom,4326)) AS lon,
                ST_Y(ST_Transform(ani_points.next_geom,4326)) AS lat,
                DATE '1970-01-01' + (ani_points.next_temps - DATE_TRUNC('day', ani_points.next_temps)) AS temps
        FROM """+head+"""ppa_default AS ani_points
        WHERE ani_points.next_id_traj = """+str(id_traj_1)+"""
        AND ani_points.next_geom IS NOT NULL 
        AND ani_points.next_temps IS NOT NULL

        union all

        SELECT 
                hum_points.id_point, 
                hum_points.id_traj,
                hum_points.geom,
                ST_X(ST_Transform(hum_points.geom,4326)) AS lon,
                ST_Y(ST_Transform(hum_points.geom,4326)) AS lat,
                DATE '1970-01-01' + (hum_points.temps - DATE_TRUNC('day', hum_points.temps)) AS temps


        FROM """+head+"""hda_default AS hum_points
        WHERE hum_points.id_traj = """+str(id_traj_2)+"""
        AND hum_points.geom IS NOT NULL 
        AND hum_points.temps IS NOT NULL

        UNION

        SELECT 
                hum_points.next_id_point, 
                hum_points.next_id_traj,
                hum_points.next_geom,
                ST_X(ST_Transform(hum_points.next_geom,4326)) AS lon,
                ST_Y(ST_Transform(hum_points.next_geom,4326)) AS lat,
                DATE '1970-01-01' + (hum_points.next_temps - DATE_TRUNC('day', hum_points.next_temps)) AS temps
        FROM """+head+"""hda_default AS hum_points
        WHERE hum_points.next_id_traj = """+str(id_traj_2)+"""
        AND hum_points.next_geom IS NOT NULL 
        AND hum_points.next_temps IS NOT NULL

        ORDER BY id_traj, temps;
    """


    dat = sqlio.read_sql_query(qurry, con)


    interactio = ot.ORTEGA(data=dat,
                        minute_max_delay=5,
                        latitude_field='lat',
                        longitude_field='lon',
                        time_field='temps',
                        id_field='id_traj')

    interactio.compute_ppa_perimeter()
    interactio.compute_ppa_interval()
    interactio.compute_ppa_area()
    interactio.compute_ppa_speed()

    interactio.compute_ppa_perimeter()
    os.system('cls')

    res = interactio.interaction_analysis()

    if res == None:
        return 0
    else:
        interactions = res.df_interaction_events

        return len(interactions)


for run in runs:
        
    min_min_dist = run[0]
    max_min_dist = run[1]

    curs = con.cursor()

    curs.execute("""	
    select b_.id_traj, b_.id_traj_2, min(a_.min_dist)
    from """+head+"""encounter_default as a_ 
    left join 	(select 
                    distinct on (id_encounter) 
                    id_encounter, 
                    id_traj, 
                    id_traj_2
                from """+head+"""encounter_event_default) as b_
        on a_.id_encounter = b_.id_encounter 
    group by b_.id_traj, b_.id_traj_2
    having min(a_.min_dist) < """+str(max_min_dist)+"""
    and min(a_.min_dist) >= """+str(min_min_dist)+"""
    order by min(a_.min_dist)
    """)


    ids = curs.fetchall()


    encounters = ids

    res = []
    len_ = len(encounters)

    i = 0
    for traj,traj_2,dist in encounters:
        holder = tfo_with_filtering(traj, traj_2, con)
        res.append(holder)
        i += 1
        print(str(i)+'/'+str(len_))

    res.count(0)/len(res)
    a,b,c = ([ a for a,b,c in encounters ], [ b for a,b,c in encounters ],[ float(c) for a,b,c in encounters ])
    to_save = list(zip(a,b,c,res))
    with open('ortegra_res_'+str(min_min_dist)+'_'+str(max_min_dist)+'.txt', 'w') as f:
        for line in to_save:
            f.write(str(line)+',')

# %%

import re
import pandas as pd

min_min_dist = 1
max_min_dist = 25

# Read the file
with open('ortegra_res_'+str(min_min_dist)+'_'+str(max_min_dist)+'.txt', 'r') as f:
    data = f.read()

# Strict regex: (int, int, float, 0 or 1)
pattern = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d]+\.[\d]+)\s*,\s*([01])\s*\)'
matches = re.findall(pattern, data)

print(f"Found {len(matches)} valid tuples.")

# Convert matches to proper types
df = pd.DataFrame(matches, columns=['col1','col2','col3','col4'])
df = df.astype({'col1': int, 'col2': int, 'col3': float, 'col4': int})

print(df.head())
print(f"Unique values in col4: {df['col4'].unique()}")

percent_ones = (df['col4'] == 1).mean() * 100
print(f"Percent of 1s in col4: {percent_ones:.2f}%")

# %% 

# Open both files in read mode
with open('ortegra_res_0_1.txt', 'r') as file1, open('ortegra_res_1_25.txt', 'r') as file2:
    # Read all lines from both files
    data1 = file1.readlines()
    data2 = file2.readlines()
    
# Append the content of file2 to file1
merged_data = data1 + data2

# Save the merged content to a new file
with open('ortegra_res_0_25.txt', 'w') as merged_file:
    merged_file.writelines(merged_data)

print("Files merged successfully!")



# %%

rows = []

runs = [[0,25],[25,50],[50,75]]

for min_min_dist, max_min_dist in runs:
    filename = f"ortegra_res_{min_min_dist}_{max_min_dist}.txt"
    
    with open(filename, 'r') as f:
        data = f.read()

    pattern = r'\(\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d]+\.[\d]+)\s*,\s*([01])\s*\)'
    matches = re.findall(pattern, data)

    df = pd.DataFrame(matches, columns=['col1','col2','col3','col4'])
    df = df.astype({'col1': int, 'col2': int, 'col3': float, 'col4': int})

    rows.append({
        'min_dist': min_min_dist,
        'max_dist': max_min_dist,
        'percent_1s': (df['col4'] == 1).mean() * 100
    })

summary_df = pd.DataFrame(rows)

summary_df

# %%
