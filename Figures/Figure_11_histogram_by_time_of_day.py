# %%
import sys
import os

import psycopg2
import matplotlib.pyplot as plt

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

folder_path = r"ADD PATH TO TRACKLIB FOLDER"

if folder_path not in sys.path:
    sys.path.insert(0, folder_path)

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

curs = conn.cursor()

curs.execute("""	

SELECT 
    c_.id_encounter,
    min(b_.temps_2) as earliest,
    max(b_.next_temps_2) as latest,
    CASE
        WHEN EXTRACT(MONTH FROM c_.date_animal) BETWEEN 3 AND 5  THEN 'Spring'
        WHEN EXTRACT(MONTH FROM c_.date_animal) BETWEEN 6 AND 8  THEN 'Summer'
        WHEN EXTRACT(MONTH FROM c_.date_animal) BETWEEN 9 AND 11 THEN 'Fall'
        WHEN EXTRACT(MONTH FROM c_.date_animal) IN (12, 1, 2)	THEN 'Winter'
        ELSE 'Unknown'
    END AS season
FROM """+source_table_events+""" as b_
inner join """+encounter_table+"""  as c_
    on	b_.id_encounter = c_.id_encounter
where   c_.vis is True
group by c_.id_encounter
  """)


ids = curs.fetchall()
print('len of ids = ' +str(len(ids)))
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
    
    print(np.sum(traj_count_in_bins))      
    epee = [int(ep) for ep in traj_count_in_bins]
    bin_centers = (bins[:-1] + bins[1:]) / 2
    expanded = np.repeat(bin_centers, epee)
    ax.bar(bin_centers, traj_count_in_bins, width=(bins[1] - bins[0]), align='center', edgecolor='k', color='blue')
    normalized_counts = traj_count_in_bins / np.max(traj_count_in_bins)
    ax.bar(bin_centers, normalized_counts, width=(bins[1] - bins[0]), align='center', edgecolor='k', color='skyblue')
    
    
    x = np.linspace(0, 24 * 60, 1000)  # Generate x values over the range of encounter times
    median_1.append(np.median(expanded))

    if i == 1 or i == 3:
        ax.yaxis.set_visible(False)

    ax.set_title(f"{season_} : Median Enc = {int(median_1[i] // 60)}h{int(median_1[i] % 60):02}", fontsize=23)
    
    if i == 2 or i == 3:
        ax.set_xlabel('Time of Day (h)', fontsize=20)
    ax.set_ylabel('Number of Active Trajectories', fontsize=20)
    ax.set_xlim(0, 24 * 60)
    #ax.set_ylim(0,7500)
    ax.set_xticks(np.arange(0, 24 * 60, 120))
    ax.set_xticklabels([f"{h:02}" for h in range(0, 24, 2)])


plt.tight_layout()
plt.show()

# %%
