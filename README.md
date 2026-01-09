# Human_Wildlife_Encounter_Detection
This repository contains the code, and scripts necessary to reproduce the analyses and figures presented in 'A New Spatio-Temporal Method for Detecting Human-Wildlife Encounters from GNSS Trajectories' submitted to Agile.

# Restore Database
This section provides a step by step prosses to restore the database using PGadmin4. After installing PGadmin4. When opening Pgadmin4 you may receive a password prompt for a password set during the installation. 

The first step is to create a new database by right clicking database tab, hover over 'create' and select 'database'.

<img width="605" height="251" alt="DB_1_create_db_blocks" src="https://github.com/user-attachments/assets/16db8eb7-67c4-46b2-a8b1-ebd736c0b5e6" />

The following prompt will appear where you must give the data base a name. Here I use ‘ResRoute’ which is used in the accompanying code as the default database name. Then click save.

<img width="605" height="451" alt="DB_2_create_db_2" src="https://github.com/user-attachments/assets/0cabb8c6-9016-419e-b6cc-917fe559797b" />

Next download the data by going to the OSF link included in the paper submission under Data and Software Availability. Download the files as a zip and extract the folder. 

Download ‘0_Create_and_Populate_Database.sql’ file from this github project and update the file paths to the location you extracted the data. This can be easily done in a a text editor with find and replace.

Find : ‘ADD PATH TO DATA FILES => ’

Replace: The path to your folder 

<img width="1325" height="697" alt="download_data_arrow" src="https://github.com/user-attachments/assets/05bc0bc1-2e4b-47f6-867f-72cafb7b8a2c" />


This should update all file paths automatically. Alternatively manually update the 15 locations.

<img width="1308" height="753" alt="update_file_paths drawio" src="https://github.com/user-attachments/assets/1b444aed-3f8f-42bc-b73e-510fbeb33f0c" />

After updating the file paths run ‘0_Create_and_Populate_Database.sql’ in the ‘PSQL Tool’. To do this right click the database name and select ‘PSQL Tool’. Check that the path is correct the database name should appear at the end of the command window followed by ‘=#’. Run the following two lines of code update with the path to where you saved the updated ‘0_Create_and_Populate_Database.sql’.

<img width="605" height="231" alt="DB_3_open_scratchpad" src="https://github.com/user-attachments/assets/ca2277cb-a3b0-44de-96b6-07b8937b0eea" />

\cd ‘Path to the folder with 0_Create_and_Populate_Database.sql '

\i 0_Create_and_Populate_Database.sql

