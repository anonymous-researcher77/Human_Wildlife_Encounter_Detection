# Human_Wildlife_Encounter_Detection
This repository contains the code, and scripts necessary to reproduce the analyses and figures presented in 'A New Spatio-Temporal Method for Detecting Human-Wildlife Encounters from GNSS Trajectories' submitted to Agile.

The first step is to download and extract the files included in this github project.

# Restore Database
This section provides a step by step prosses to restore the database using PGadmin4. You can install PGadmin4 or use your prefeared SQL method though the step by step gide is done using PGadmin4. When opening Pgadmin4 you may receive a password prompt for a password set during the installation. 

The first step is to create a new database by right clicking database tab, hover over 'create' and select 'database'.

<img width="605" height="251" alt="DB_1_create_db_blocks" src="https://github.com/user-attachments/assets/16db8eb7-67c4-46b2-a8b1-ebd736c0b5e6" />

The following prompt will appear where you must give the data base a name. Here I use ‘ResRoute’ which is used in the accompanying code as the default database name. Then click save.

<img width="605" height="451" alt="DB_2_create_db_2" src="https://github.com/user-attachments/assets/0cabb8c6-9016-419e-b6cc-917fe559797b" />

Next download the data by going to the OSF link included in the paper submission under Data and Software Availability. Download the files as a zip and extract the folder. 

Download ‘0_Create_and_Populate_Database.sql’ file from this github project if not already done and update the file paths in ‘0_Create_and_Populate_Database.sql’ to the location you extracted the data. This can be easily done in a a text editor with find and replace.

Find : ‘ADD PATH TO DATA FILES => ’

Replace: The path to your folder containing the data 

<img width="1325" height="697" alt="download_data_arrow" src="https://github.com/user-attachments/assets/05bc0bc1-2e4b-47f6-867f-72cafb7b8a2c" />


This should update all file paths automatically. Alternatively manually update the 15 locations.

<img width="1308" height="753" alt="update_file_paths drawio" src="https://github.com/user-attachments/assets/1b444aed-3f8f-42bc-b73e-510fbeb33f0c" />

After updating the file paths run ‘0_Create_and_Populate_Database.sql’ in the ‘PSQL Tool’. To do this right click the database name and select ‘PSQL Tool’. Check that the path is correct the database name should appear at the end of the command window followed by ‘=#’. Run the following two lines of code update with the path to where you saved the updated ‘0_Create_and_Populate_Database.sql’.

<img width="1915" height="1002" alt="DB_3_open_scratchpad_2" src="https://github.com/user-attachments/assets/f29ff201-28c7-4565-b630-afdf66eeb91f" />

<img width="1905" height="1002" alt="DB____55" src="https://github.com/user-attachments/assets/17db4640-7c1d-46d6-9cb5-c367b7760b57" />

\i PATH/TO/FILE/0_Create_and_Populate_Database.sql

The expected runtime is about 

The final output will look like this.

# Create python environment

Here I will use Visual Studio Code and jupiter note books.

The first step is to create a vertual environment to do this in the folder that you downloaded the github project.

In Visual Studio Code open the folder containing the project

Using 'ctrl + shift + p' then select interpreter and select you python instelation. See image below.


<img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/d36c9456-5d20-413f-8517-b6e21a2e3196" />

<img width="1923" height="491" alt="image" src="https://github.com/user-attachments/assets/58a27b81-12ff-4dbf-bfeb-ec6ce0e0a01d" />

Then using 'ctrl + shift + p' then select 'Python: Create Environment...' followed by 'Venu' followed by 'Python #.#.#'

<img width="1927" height="527" alt="image" src="https://github.com/user-attachments/assets/a56473d0-cc6e-421d-ad64-5a0b98eacccd" />

<img width="1919" height="485" alt="image" src="https://github.com/user-attachments/assets/f6540315-4566-4351-bd20-c17f83dd231a" />

<img width="1918" height="383" alt="image" src="https://github.com/user-attachments/assets/85b76a9c-2b06-4c1b-9c74-e96b674e1df3" />

Followed by this you must install the required libraries. open the terminal using 'ctrl + shift + ù' and pip install the all libraries in the requirments file.

<img width="1916" height="1009" alt="the_requirments" src="https://github.com/user-attachments/assets/ce881440-2ba7-4499-8ebd-71b94fed1e8c" />

The next step is run in python and needs to have files arranged properly. Download the 

<img width="1920" height="877" alt="install_requirments" src="https://github.com/user-attachments/assets/e8dc494e-18d6-450f-878e-b1c912bcd3a1" />

Finally Tracklib is not able to be installed using pip so you must download and extract Tracklib from the following link https://github.com/umrlastig/tracklib.

# Create Encounter Events

Next to create the encounter events tables in the database you must edite acouple lines in the '1_main_Create_Encounter_Events.py' file. The tracklib_folder_path variable must be replaced with the path where you extracted tracklib and the 'db' must be the database name, 'db_user' is the name of the user of the database and 'db_password' must be the pasword to the database if they differ from the 'ResRoute' or the defaults of 'postgres' and 'postgres'.   

Then if you click 'Run Below' it will create the Encounter Events tables for each set of variables used in the paper. 

<img width="1922" height="1008" alt="encounter_events_111" src="https://github.com/user-attachments/assets/c8fc38ff-a4a7-4b5a-b98c-3dc792b4840b" />

The total expected run tile is ____
+ Default: Create Encounter Events  
+ HDA = 500: Create Encounter Events
+ d_gap_a = 999999999: Create Encounter Events
+ d_gap_h = 999999999: Create Encounter Events


# Run Intervisibility

The file '2_Intervisibility.py' must be run in a QGIS environment. To do this open QGIS and select the 'python consol' using the icon in the image below or by using 'ctrl + alt + p'.

<img width="1922" height="1005" alt="QGIS_1" src="https://github.com/user-attachments/assets/4047096a-ef58-4817-8bc9-221db96d4842" />

Open the '2_Intervisibility.py' file using the 'open script...' icon shown below

<img width="1915" height="1027" alt="QGIS_2" src="https://github.com/user-attachments/assets/422ad702-1aad-47eb-af09-55793a6327d4" />

After opening the file the path to the dem must be updated and then to run the file set run all to true or uncomment one of the predefind sets of variables. QGIS is not stable while running such a large calculation and may freeze during the run. I have found that uncommenting and running the intervisibilety check one at a time is more stable.

<img width="1919" height="1029" alt="QGIS_3" src="https://github.com/user-attachments/assets/d9882811-a017-4695-9426-249d1ef7c5f9" />

After selecting a method click the green arrow to run the code.

<img width="1907" height="1028" alt="QGIS_4" src="https://github.com/user-attachments/assets/7bcc65e4-d6ac-4cf9-9a78-802a433d0738" />

# Create Encounters

# Run Figures

# Run Tables


