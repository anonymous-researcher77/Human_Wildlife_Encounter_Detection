# %%

import matplotlib.pyplot as plt
import sys
import os

main_folder_path    = os.path.dirname(os.path.dirname(__file__))

if main_folder_path not in sys.path:
    sys.path.insert(0, main_folder_path)

import my_utils_plotting 


db      = 'ResRoute'
db_connection_url = "postgresql://postgres:postgres@localhost:5432/"+db

head    = 'exp__'
end     = '_default'
when 	= 'all'
season 	= 'all'
r_p 	= 'all'
spotting_table 	= 'exp__encounter_event_hda_500'     # head+'encounter_event'+end
encounter_table = 'exp__encounter_ignore_vis_hda_500'# head+'encounter'+end
traj_int 		= head+'traj_ints'+end

# %%

dbs1 = my_utils_plotting.querry_enc_fig_9(spotting_table,
                 encounter_table,
                  time = when,
                  season = season, 
                  r_p = r_p,
                  vis = True,
                  db = db,
                db_connection_url = db_connection_url)

dbs2 = my_utils_plotting.querry_enc_fig_9(spotting_table,
                 encounter_table,
                  time = when,
                  season = season, 
                  r_p = r_p,
                  id_column = 'id_encounter_ignore_vis',
                  vis = False,
                  db = db,
                  db_connection_url = db_connection_url)

fig, ax = plt.subplots(figsize=(10, 10))

plt.rcParams.update({'font.size': 20})


# Fetch all the results from the query

min_distances1 = [item for item in dbs1['min_dist']]
min_distances2 = [item for item in dbs2['min_dist']]

# Create a list to store the grouped encounter times for each season
tmp = []

tmp.append(min_distances1)
tmp.append(min_distances2)

# Plot the stacked histogram
#(n, bins, patches)= ax.hist(tmp, bins=48, stacked=True,edgecolor = 'k', color=['g', 'r'], alpha=0.73)

# Define custom bins: 0 and then 1-25, 25-50, ..., 475-500
bins = [0, 1, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400, 425, 450, 475, 500, 525]

# Plot the histogram with the custom bins
(n, bins, patches)= ax.hist(tmp, bins=bins, stacked=True, edgecolor = 'k', color=['b', 'r'], alpha=0.73)

# Add a callout for the 0 value (if any)

ax.set_ylim(0,12500)

ax.legend(['Visibility','Visibility blocked'])

# Add labels and title with correct spelling
plt.xlabel('Minimum HDA_radius required [meters]')  # Corrected label
plt.ylabel('Number of Encounters')  # Corrected label

# Set custom ticks on the x-axis
plt.xticks([0, 100, 200, 300, 400, 500])
ax.set_xlim(0,500)

plt.tight_layout()
plt.show()


# %%
