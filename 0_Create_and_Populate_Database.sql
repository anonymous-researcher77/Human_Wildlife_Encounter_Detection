-- Drop database if exists
DROP TABLE IF EXISTS Species CASCADE;
DROP TABLE IF EXISTS trajectories_indivs CASCADE;
DROP TABLE IF EXISTS Recorded_Animal CASCADE;
DROP TABLE IF EXISTS indiv_Human CASCADE; 
DROP TABLE IF EXISTS trajectories CASCADE;
DROP TABLE IF EXISTS Goal CASCADE;
DROP TABLE IF EXISTS sub_trajectories CASCADE;
DROP TABLE IF EXISTS points CASCADE;
DROP TABLE IF EXISTS activity CASCADE;
DROP TABLE IF EXISTS Environment CASCADE;
DROP TABLE IF EXISTS Movment CASCADE;

DROP TYPE IF EXISTS goal_type CASCADE;
DROP TYPE IF EXISTS activity_type CASCADE;
DROP TYPE IF EXISTS environment_type CASCADE;
DROP TYPE IF EXISTS move_type CASCADE;

-- Adds postgis
CREATE EXTENSION postgis;

CREATE TABLE Species(id_species SERIAL PRIMARY KEY, name varchar(255) UNIQUE, alert_distance integer, flight_distnce integer, conservation varchar(255));

CREATE TABLE trajectories_indivs(id_indiv SERIAL PRIMARY KEY, type_indiv varchar(255));--, hidden_name varchar(255) unique);

CREATE TABLE Recorded_Animal(id_indiv integer REFERENCES trajectories_indivs (id_indiv) unique, id_species integer REFERENCES Species (id_species),    source varchar(255) NOT NULL,    birth_year integer,    gender varchar(255));

CREATE TABLE indiv_Human( id_indiv integer REFERENCES trajectories_indivs (id_indiv) unique, source varchar(255) NOT NULL, birth_year integer, gender varchar(255));

CREATE TABLE trajectories( id_traj SERIAL PRIMARY KEY, id_indiv integer REFERENCES trajectories_indivs (id_indiv), date date, count_points integer, count_outlier integer, count_missing_geom integer, count_missing_temps integer, spatial_granularity numeric, temporal_granularity numeric, geom geometry);

CREATE TYPE Goal_type AS ENUM ('h_hunt', 'h_mointain_bike', 'h_ski', 'h_hike', 'h_run', 'h_backcountryski', 'a_seasonal_migration', 'h_alpineski');

CREATE TABLE Goal( id_goal SERIAL PRIMARY KEY, id_traj integer REFERENCES trajectories (id_traj), goal_type Goal_type, declared boolean);

CREATE TABLE sub_trajectories( id_sub_traj SERIAL PRIMARY KEY, id_traj integer REFERENCES trajectories (id_traj), start_time time, end_time time, geom geometry);

CREATE TABLE points( id_point SERIAL PRIMARY KEY, id_sub_traj integer REFERENCES sub_trajectories (id_sub_traj), geom geometry, temps timestamp without time zone, outlier boolean);

CREATE TYPE Activity_type AS ENUM ( '0', '1', '2', '3', 'a_diel_migration', 'a_forage', 'a_flee', 'a_travel', 'a_rest', 'a_sunbath', 'h_off_trail', 'h_move_toward_exit', 'h_breath_catching_stop', 'h_move_toward_poi');

CREATE TYPE Environment_type AS ENUM ('None/Aucun', 'Woods/Bois', 'Closed coniferous forest/Forêt fermée de conifères', 'Closed deciduous forest/Forêt fermée de feuillus', 'Mixed closed forest/Forêt fermée mixte', 'Open forest/Forêt ouverte', 'Hedge/Haie', 'Woody heath/Lande ligneuse', 'Poplar grove/Peupleraie', 'Orchard/Verger', 'Vineyard/Vigne');

CREATE TYPE Move_type AS ENUM ('walk', 'bike', 'car');

CREATE TABLE activity(id_sub_traj integer REFERENCES sub_trajectories (id_sub_traj), activity_type Activity_type);

CREATE TABLE environment(id_sub_traj integer REFERENCES sub_trajectories (id_sub_traj), environment_type Environment_type);

CREATE TABLE movment(id_sub_traj integer REFERENCES sub_trajectories (id_sub_traj), move_type Move_type);

\COPY Species 	 			    FROM 'ADD PATH TO DATA FILES => /Species.csv'  			CSV HEADER DELIMITER ',';
\COPY trajectories_indivs	FROM 'ADD PATH TO DATA FILES => /trajectories_indivs.csv' CSV HEADER DELIMITER ',';
\COPY Recorded_Animal		  FROM 'ADD PATH TO DATA FILES => /Recorded_Animal.csv'  	CSV HEADER DELIMITER ',';
\COPY indiv_Human			    FROM 'ADD PATH TO DATA FILES => /indiv_Human.csv'  		CSV HEADER DELIMITER ',';
\COPY trajectories			  FROM 'ADD PATH TO DATA FILES => /trajectories.csv'  		CSV HEADER DELIMITER ',';

\COPY Goal     	 			    FROM 'ADD PATH TO DATA FILES => /Goal.csv'				CSV HEADER DELIMITER ',';
\COPY sub_trajectories		FROM 'ADD PATH TO DATA FILES => /sub_trajectories.csv'  	CSV HEADER DELIMITER ',';


\COPY points 		    FROM 'ADD PATH TO DATA FILES => /points.bin' BINARY;
--\COPY points 		  FROM 'ADD PATH TO DATA FILES => /points.csv' 		CSV HEADER DELIMITER ',';
\COPY activity  	  FROM 'ADD PATH TO DATA FILES => /activity.csv' 	CSV HEADER DELIMITER ',';
\COPY environment   FROM 'ADD PATH TO DATA FILES => /environment.csv' CSV HEADER DELIMITER ',';
\COPY movment      	FROM 'ADD PATH TO DATA FILES => /movment.csv' 	CSV HEADER DELIMITER ',';


CREATE TABLE edges_import (  id_edge     INTEGER,  first_node  INTEGER,second_node INTEGER,geom_wkt    TEXT,count_traj  INTEGER);
CREATE TABLE edges (  id_edge     INTEGER,  first_node  INTEGER,second_node INTEGER,geom    geometry ,count_traj  INTEGER);

\COPY edges_import FROM 'ADD PATH TO DATA FILES => /edges.csv' WITH (   FORMAT CSV,   HEADER TRUE,   DELIMITER ',',   QUOTE '"',   ESCAPE '"' );

SELECT COUNT(*) FROM edges_import;

INSERT INTO edges (id_edge, first_node, second_node, geom, count_traj) SELECT  id_edge,  first_node,  second_node,  ST_GeomFromText(geom_wkt, 2056),     count_traj FROM edges_import;

SELECT COUNT(*) FROM edges;

DROP TABLE edges_import;


CREATE TABLE bauges_import (  id    INTEGER,  geom_wkt    TEXT, limite_res  TEXT);


\COPY bauges_import FROM 'ADD PATH TO DATA FILES => /bauges.csv' WITH (   FORMAT CSV,   HEADER TRUE,   DELIMITER ',',   QUOTE '"',   ESCAPE '"' );

CREATE TABLE bauges(  id    INTEGER,  geom    geometry, limite_res  TEXT);
INSERT INTO bauges (id, geom, limite_res) SELECT  id,  ST_GeomFromText(geom_wkt, 2056), limite_res FROM bauges_import;
DROP TABLE bauges_import;


CREATE TABLE france_import (id INTEGER, geom_wkt TEXT, fid bigint);
CREATE TABLE france (id INTEGER, geom geometry, fid bigint);

\COPY france_import FROM 'ADD PATH TO DATA FILES => /france.csv' WITH (   FORMAT CSV,   HEADER TRUE,   DELIMITER ',',   QUOTE '"',   ESCAPE '"' );

SELECT COUNT(*) FROM france_import;

INSERT INTO france (id, geom, fid) SELECT  id, ST_GeomFromText(geom_wkt, 2056), fid FROM france_import;

SELECT COUNT(*) FROM france;

DROP TABLE france_import;

