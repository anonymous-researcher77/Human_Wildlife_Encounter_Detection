# Human_Wildlife_Encounter_Detection
This repository contains the code and scripts necessary to reproduce the analyses and figures presented in 'A New Spatio-Temporal Method for Detecting Human-Wildlife Encounters from GNSS Trajectories' submitted to Agile.

The first step is to download and extract the files included in this github project.

# Restore Database
This section provides a step by step process to restore the database using PGadmin4. You can install PGadmin4 or use your prefered SQL method though the step by step guide is done using PGadmin4. When opening Pgadmin4, you may receive a password prompt for a password set during the installation. 

The first step is to create a new database by right clicking database tab, hover over 'create' and select 'database'.

<img width="605" height="251" alt="DB_1_create_db_blocks" src="https://github.com/user-attachments/assets/16db8eb7-67c4-46b2-a8b1-ebd736c0b5e6" />

The following prompt will appear where you must give the database a name. Here I use ‘ResRoute’ which is used in the accompanying code as the default database name. Then click save.

<img width="605" height="451" alt="DB_2_create_db_2" src="https://github.com/user-attachments/assets/0cabb8c6-9016-419e-b6cc-917fe559797b" />

Next, download the data by going to the OSF link included in the paper submission under Data and Software Availability. Download the files as a Zip and extract the folder. 

<img width="1325" height="697" alt="download_data_arrow" src="https://github.com/user-attachments/assets/05bc0bc1-2e4b-47f6-867f-72cafb7b8a2c" />


Download ‘0_Create_and_Populate_Database.sql’ file from this github project if not already done and update the file paths in ‘0_Create_and_Populate_Database.sql’ to the location you extracted the data. This can be easily done in a text editor with find and replace.

Find : ‘ADD PATH TO DATA FILES => ’

Replace: The path to your folder containing the data 
This should update all file paths automatically. Alternatively manually update the 15 locations.

<img width="1308" height="753" alt="update_file_paths drawio" src="https://github.com/user-attachments/assets/1b444aed-3f8f-42bc-b73e-510fbeb33f0c" />

After updating the file paths, run ‘0_Create_and_Populate_Database.sql’ in the ‘PSQL Tool’. To do this, right click the database name and select ‘PSQL Tool’. Check that the path is correct. The database name should appear at the end of the command window followed by ‘=#’. Run the following line of code update with the path to where you saved the updated ‘0_Create_and_Populate_Database.sql’.

\i PATH/TO/FILE/0_Create_and_Populate_Database.sql

<img width="1915" height="1002" alt="DB_3_open_scratchpad_2" src="https://github.com/user-attachments/assets/f29ff201-28c7-4565-b630-afdf66eeb91f" />

<img width="1905" height="1002" alt="DB____55" src="https://github.com/user-attachments/assets/17db4640-7c1d-46d6-9cb5-c367b7760b57" />


The expected runtime is about 

The final output will look like this.

# Create a python environment

Here I will use Visual Studio Code and Jupyter Notebook.

The first step is to create a virtual environment. 

In Visual Studio Code, open the folder containing the project.

Use 'ctrl + shift + p' then select 'Interpreter' and select your python installation. See images below.


<img width="1867" height="837" alt="hide_identity_nom drawio" src="https://github.com/user-attachments/assets/85216393-20b1-43a9-94fd-efd6d1d4fad7" />

<img width="1923" height="491" alt="image" src="https://github.com/user-attachments/assets/58a27b81-12ff-4dbf-bfeb-ec6ce0e0a01d" />

Then use 'ctrl + shift + p' to select 'Python: Create Environment...' followed by 'Venu' followed by 'Python #.#.#'

<img width="1877" height="879" alt="image" src="https://github.com/user-attachments/assets/289583cc-0310-48c3-9ef6-42add65cd05b" />


<img width="1919" height="485" alt="image" src="https://github.com/user-attachments/assets/f6540315-4566-4351-bd20-c17f83dd231a" />

<img width="1918" height="383" alt="image" src="https://github.com/user-attachments/assets/85b76a9c-2b06-4c1b-9c74-e96b674e1df3" />

Followed by this, you must install the required libraries. Open the terminal using 'ctrl + shift + ù' and pip install all the libraries in the 'requirements' file.

<img width="1916" height="1009" alt="the_requirments" src="https://github.com/user-attachments/assets/ce881440-2ba7-4499-8ebd-71b94fed1e8c" />

<img width="1920" height="877" alt="install_requirments" src="https://github.com/user-attachments/assets/e8dc494e-18d6-450f-878e-b1c912bcd3a1" />

Tracklib is not able to be installed using pip, so you must download and extract Tracklib from the following link https://github.com/umrlastig/tracklib.

Finally the file 'my_utils.py' must be updated. the variable folder_path = r"ADD PATH TO TRACKLIB FOLDER e.x. => \tracklib" must be updated to the path where Tracklib has been extracted.

# Create Encounter Events

Next, to create the encounter events tables in the database, you must edit a couple of lines in the '1_main_Create_Encounter_Events.py' file. The tracklib_folder_path variable must be replaced with the path where you extracted tracklib. If your database does not use the preset values listed here you must update the variables to match your database.

- 'db' is the name of the database
- 'db_user' is the name of the user of the database
- 'db_password' must be the password to the database


Then if you click 'Run Below', it will create the Encounter Events tables for each set of variables used in the paper. 

<img width="1922" height="1008" alt="encounter_events_111" src="https://github.com/user-attachments/assets/c8fc38ff-a4a7-4b5a-b98c-3dc792b4840b" />

The total expected run time is ____
+ Default: Create Encounter Events  
+ HDA = 500: Create Encounter Events
+ d_gap_a = 999999999: Create Encounter Events
+ d_gap_h = 999999999: Create Encounter Events


# Run Intervisibility

The file '2_Intervisibility.py' must be run in a QGIS environment. To do this, open QGIS and select the 'python console' using the icon in the image below or by using 'ctrl + alt + p'.

<img width="1922" height="1005" alt="QGIS_1" src="https://github.com/user-attachments/assets/4047096a-ef58-4817-8bc9-221db96d4842" />

Open the '2_Intervisibility.py' file using the 'open script...' icon shown below

<img width="1915" height="1027" alt="QGIS_2" src="https://github.com/user-attachments/assets/422ad702-1aad-47eb-af09-55793a6327d4" />

<img width="1919" height="1029" alt="QGIS_3" src="https://github.com/user-attachments/assets/d9882811-a017-4695-9426-249d1ef7c5f9" />

After opening the file, the path to the dem must be updated and then, to run the file, set run all to true or uncomment one of the predefined sets of variables. QGIS is not stable while running such a large calculation and may freeze during the run. I have found that uncommenting and running the intervisibility check one at a time is more stable.


After selecting a method, click on the green arrow to run the code.

<img width="1907" height="1028" alt="QGIS_4" src="https://github.com/user-attachments/assets/7bcc65e4-d6ac-4cf9-9a78-802a433d0738" />

# Create Encounters

After Intervisibility has been added for all encounter events tables encounters can be calculated by using the '3_main_Create_Encounters.py' file. '3_main_Create_Encounters.py' has the same 4 lines as '1_main_Create_Encounter_Events.py'.

- tracklib_folder_path must be set to the path to where tracklib is loaded
- 'db' is the name of the database
- 'db_user' is the name of the user of the database
- 'db_password' must be the password to the database
  
<img width="1860" height="901" alt="enounters___" src="https://github.com/user-attachments/assets/3bae29d7-bdb5-453c-987b-17bc2665ed23" />

After updating the required lines the click 'run below' at the top cell this will execute all cells creating encounter events of all settings used in the paper.

Expected total run time is ____
- default settings
- HDA = 500
- d_gap_h = None
- d_gap_a = None
- t_gap = 2 min
- t_gap = 4 min
- t_gap = 16 min
- t_gap = 2 hours
- t_gap = 4 hours
- t_gap = 24 hours
- height_chamois = 0.8 m
- height_chamois = 1.2 m
- height_human = 2 m
- Ignoring intervisibility
- Ignoring intervisibility hda = 500

# Run Figures

After creating the encounter tables to recreate the results from the paper figures can be created by running the various figure python folders. Only figures that include results or data are included here. Diagram figures that do not use data are not included.

**Figure_8_data_map.py**

This file only requires that the database path is accurate i.e. the following are accurate
- db = 'ResRoute'
- db_connection_url =
    
**Figure_9_Depiction_of_ECA.py**

This file only requires that the database path is accurate i.e. the following are accurate
- db = 'ResRoute'
- db_connection_url =
    
**Figure_10_histogram_by_distance.py**

This file only requires that the database path is accurate i.e. the following are accurate
- db = 'ResRoute'
- db_connection_url =
  
**Figure_11_histogram_by_time_of_day.py**

This file requires that the following are updated
- file path to tracklib
- db = 'ResRoute'
- db_connection_url =

**Figure_12_kernel_density_estimate.py**

This file requires that the following are updated if they do not match the defaults
- db = 'ResRoute'
- db_user = 'postgres'
  
**Figure_13_seasons_heatmap.py**

This file requires the following to be update
- folder_path =        r"ADD PATH TO TRACKLIB FOLDER"
- db_connection_url   = "postgresql://postgres:postgres@localhost:5432/ResRoute"
- elevation_path      = 'ADD PATH TO ELEVATION FILE => /bouge_elev.tif'
  
# Run Tables

**Table_2_chamois_data.py**

This file requires the following to be update
- db          =  'ResRoute'
- db_user     =  'postgres'
- db_password =  'postgres'

**Table_3_human_data.py**

This file requires the following to be update
- db          =  'ResRoute'
- db_user     =  'postgres'
- db_password =  'postgres'

**Table_5_HDA_radius_and_Intervisibility.py**

This file requires the following to be update
- db          =  'ResRoute'
- db_user     =  'postgres'
- db_password =  'postgres'

**Table_6_parameters.py**

This file requires the following to be update
- db          =  'ResRoute'
- db_user     =  'postgres'
- db_password =  'postgres'

**Table_7_ORTEGA.py**

This file runs many instances of the Ortega library for comparison but forces Ortega to run pair of trajectories at a time severely affecting its optimization. To save time in recreating the table after the first run checkpoints are saved. It also has a significant run time.

If the csv of the Ortega results is already created to only rerun the table only run the first and last cells.

This file requires the following to be update
- db          =  'ResRoute'
- db_user     =  'postgres'

**Table_8_trajectories_seasons.py**

- db          =  'ResRoute'
- db_user     =  'postgres'
- db_password =  'postgres'
