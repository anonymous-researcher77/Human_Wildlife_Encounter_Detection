# %% KDE other method


import psycopg2
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt



hl = '#D8B7DD'
hm = '#800080'
hd = '#4B0082'
al = '#FFD700'
am = '#FFA500'
ad = '#FF8C00'


# %%

db      = 'ResRoute'
head    = 'exp__'
end     = '_default'
when 	= 'all'
season 	= 'all'
r_p 	= 'all'
source_table_events	= head+'encounter_event'+end
encounter_table     = head+'encounter'+end
traj_int 		    = head+'traj_ints'+end

conn = psycopg2.connect(database=db, user='postgres')


# %%

plt.rcParams.update({'font.size': 25})

curs = conn.cursor()


curs.execute("""	

SELECT 
    c_.id_encounter,
    min(b_.temps_2) as earliest,
    max(b_.next_temps_2) as latest,
    -- abs(EXTRACT(doy FROM date_animal)- EXTRACT(doy FROM date_human)) as shift,
    CASE
        WHEN EXTRACT(MONTH FROM c_.date_human) IN ( 3, 4, 5)  THEN 'Spring'
        WHEN EXTRACT(MONTH FROM c_.date_human) IN ( 6, 7, 8)  THEN 'Summer'
        WHEN EXTRACT(MONTH FROM c_.date_human) IN ( 9,10,11)  THEN 'Fall'
        WHEN EXTRACT(MONTH FROM c_.date_human) IN (12, 1, 2)  THEN 'Winter'
        ELSE 'Unknown'
    END AS season
FROM """+source_table_events+""" as b_
inner join """+encounter_table+"""  as c_
    on	b_.id_encounter = c_.id_encounter
where   b_.vis_grid is True
-- and     abs(EXTRACT(doy FROM c_.date_animal)- EXTRACT(doy FROM c_.date_human)) <=0
group by c_.id_encounter
  """)


ids = curs.fetchall()
earliest = [i[1] for i in ids]
latest = [i[2] for i in ids]
season = [i[3] for i in ids]

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# Your bins (48 bins = 30 minutes per bin)
bins = np.linspace(0, 24 * 60, 49)

# Convert lists to NumPy arrays for easier indexing
season_array = np.array(season)
start_array = np.array([(t.hour * 60 + t.minute) for t in earliest])
end_array = np.array([(t.hour * 60 + t.minute) for t in latest])

# Set up plotting
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
season_data = ['Spring', 'Summer', 'Fall', 'Winter']
median_1 = []
for i, season_ in enumerate(season_data):
    ax = axes[i // 2, i % 2]

    # Filter times for this season only
    indices = np.where(season_array == season_)[0]
    season_start_times = start_array[indices]
    season_end_times = end_array[indices]

    # Count number of trajectories active in each bin
    traj_count_in_bins = np.zeros(len(bins) - 1)

    for start_time, end_time in zip(season_start_times, season_end_times):
        start_bin = np.digitize(start_time, bins) - 1
        end_bin = np.digitize(end_time, bins) - 1

        for bin_idx in range(start_bin, end_bin + 1):
            if 0 <= bin_idx < len(traj_count_in_bins):
                traj_count_in_bins[bin_idx] += 1    
                
    epee = [int(ep) for ep in traj_count_in_bins]
    bin_centers = (bins[:-1] + bins[1:]) / 2
    expanded = np.repeat(bin_centers, epee)

    kde = gaussian_kde(expanded, bw_method=0.2)  # Bandwidth of 0.1, you can adjust this
    
    x = np.linspace(0, 24 * 60, 1000)  # Generate x values over the range of encounter times
    ax.plot(x, kde(x), color='green', lw=2)  # Plot KDE curve"""
    median_1.append(np.median(expanded))


curs = conn.cursor()


curs.execute("""	
             
    select 
        t_.id_traj, 
        st_.start_time,
        st_.end_time,
        CASE
            WHEN EXTRACT(MONTH FROM date) IN ( 3,  4,  5)  THEN 'Spring'
            WHEN EXTRACT(MONTH FROM date) IN ( 6,  7,  8)  THEN 'Summer'
            WHEN EXTRACT(MONTH FROM date) IN ( 9, 10, 11)  THEN 'Fall'
            WHEN EXTRACT(MONTH FROM date) IN (12,  1,  2)  THEN 'Winter'
            ELSE 'Unknown'
        END AS season
    from trajectories as t_
    left join (select 
                    id_traj,
                    min(start_time) as start_time,
                    max(end_time) as end_time
            from sub_trajectories
            group by id_traj) as st_
        on t_.id_traj = st_.id_traj
    inner join trajectories_indivs as ti_
        on t_.id_indiv = ti_.id_indiv
    where ti_.type_indiv = 'human'
    and st_.start_time is not null
    and NOT (st_.start_time = '00:00:00' AND st_.end_time = '00:00:00')
    """)




ids = curs.fetchall()
earliest = [i[1] for i in ids]
latest = [i[2] for i in ids]
season = [i[3] for i in ids]


# Your bins (48 bins = 30 minutes per bin)
bins = np.linspace(0, 24 * 60, 49)

# Convert lists to NumPy arrays for easier indexing
season_array = np.array(season)
start_array = np.array([(t.hour * 60 + t.minute) for t in earliest])
end_array = np.array([(t.hour * 60 + t.minute) for t in latest])

# Set up plotting
season_data = ['Spring', 'Summer', 'Fall', 'Winter']

for i, season_ in enumerate(season_data):
    ax = axes[i // 2, i % 2]

    # Filter times for this season only
    indices = np.where(season_array == season_)[0]
    season_start_times = start_array[indices]
    season_end_times = end_array[indices]

    # Count number of trajectories active in each bin
    traj_count_in_bins = np.zeros(len(bins) - 1)

    for start_time, end_time in zip(season_start_times, season_end_times):
        start_bin = np.digitize(start_time, bins) - 1
        end_bin = np.digitize(end_time, bins) - 1

        for bin_idx in range(start_bin, end_bin + 1):
            if 0 <= bin_idx < len(traj_count_in_bins):
                traj_count_in_bins[bin_idx] += 1

    # Median start time for label
    epee = [int(ep) for ep in traj_count_in_bins]
    bin_centers = (bins[:-1] + bins[1:]) / 2
    expanded = np.repeat(bin_centers, epee)

    kde = gaussian_kde(expanded, bw_method=0.1)  # Bandwidth of 0.1, you can adjust this
    x = np.linspace(0, 24 * 60, 1000)  # Generate x values over the range of encounter times
    ax.plot(x, kde(x), color= hm, lw=2)  # Plot KDE curve"""
    median_2 = np.median(expanded)
    #ax.set_title(f"{season_} : Median Enc = {int(median_1[i] // 60)}h{int(median_1[i] % 60):02} Median traj = {int(median_2 // 60)}h{int(median_2 % 60):02}")
    ax.set_title(f"{season_}")

    if i == 2 or i == 3:
        ax.set_xlabel('Time of Day (h)', fontsize=20)
    ax.set_ylabel('Number of Active Trajectories', fontsize=20)
    ax.set_xlim(0, 24 * 60)
    ax.set_ylim(-0.000025, 0.0040)

    ax.set_xticks(np.arange(0, 24 * 60, 120))
    ax.set_xticklabels([f"{h:02}" for h in range(0, 24, 2)])
    if i == 1:
        legend_elements = []
        legend_elements.append(Line2D([0], [0], color='green', lw=4, label='Encounters'))
        legend_elements.append(Line2D([0], [0], color= hm, lw=4,     label='Human Traj'))
        ax.legend(handles=legend_elements, loc='upper right')

    if i == 1 or i == 3:
        ax.yaxis.set_visible(False)


curs = conn.cursor()

curs.execute("""	

SELECT 
    c_.id_encounter,
    min(b_.temps_2) as earliest,
    max(b_.next_temps_2) as latest,
    -- abs(EXTRACT(doy FROM date_animal)- EXTRACT(doy FROM date_human)) as shift,
    CASE
        WHEN EXTRACT(MONTH FROM c_.date_human) IN (7, 8)  THEN 'Hiking'
        WHEN EXTRACT(MONTH FROM c_.date_human) IN (9, 10, 11) THEN 'Hunting'
        WHEN EXTRACT(MONTH FROM c_.date_human) IN (1, 2, 3)	THEN 'Skiing'
        ELSE 'Unknown'
    END AS season
FROM """+source_table_events+""" as b_
inner join """+encounter_table+"""  as c_
    on	b_.id_encounter = c_.id_encounter
where   b_.vis_grid is True
-- and     abs(EXTRACT(doy FROM c_.date_animal)- EXTRACT(doy FROM c_.date_human)) <=0
group by c_.id_encounter
  """)


ids = curs.fetchall()
earliest = [i[1] for i in ids]
latest = [i[2] for i in ids]
season = [i[3] for i in ids]


# Your bins (48 bins = 30 minutes per bin)
bins = np.linspace(0, 24 * 60, 49)

# Convert lists to NumPy arrays for easier indexing
season_array = np.array(season)


start_array = np.array([(t.hour * 60 + t.minute) for t in earliest])
end_array = np.array([(t.hour * 60 + t.minute) for t in latest])


plt.tight_layout()
plt.show()
