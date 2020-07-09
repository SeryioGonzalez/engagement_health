CREATE DATABASE pipeline;
USE pipeline;

CREATE TABLE engagements (engagement_id CHAR(15) NOT NULL, engagement_name CHAR(100) , monthly_acr INT , engagement_completion_date DATETIME , engagement_status INT, engagement_owner  CHAR(100), engagement_sponsor CHAR(100), engagement_partner CHAR(100), engagement_state CHAR(100), engagement_preferred_region CHAR(100), engagement_start_date DATETIME, engagement_created_date DATETIME, engagement_modified_date DATETIME, engagement_status_label CHAR(100), engagement_workload CHAR(100), engagement_solution_area CHAR(100), engagement_health_label CHAR(100), engagement_account_id CHAR(100),  PRIMARY KEY(engagement_id));
CREATE TABLE milestones  (milestone_id CHAR(15)  NOT NULL,  milestone_name CHAR(100),  engagement_id CHAR(15), monthly_acr INT, milestone_date DATETIME, milestone_status CHAR(20), PRIMARY KEY(milestone_id));

CREATE TABLE owners   (field_id CHAR(100), field_name CHAR(100), owner_role CHAR(20), PRIMARY KEY(field_id));
CREATE TABLE sponsors (field_id CHAR(100), field_name CHAR(100), PRIMARY KEY(field_id));
CREATE TABLE partners (field_id CHAR(100), field_name CHAR(100), PRIMARY KEY(field_id));

REPLACE INTO owners (field_name, owner_role) VALUES ('Jose Domingo García-Caro García', 'PSS');
REPLACE INTO owners (field_name, owner_role) VALUES ('Juan Carlos Rodríguez García', 'PSS');
REPLACE INTO owners (field_name, owner_role) VALUES ('Daniel Olaso', 'PSS');
REPLACE INTO owners (field_name, owner_role) VALUES ('Norman Ebling', 'CSA');
REPLACE INTO owners (field_name, owner_role) VALUES ('Sergio Gonzalez', 'CSA');
REPLACE INTO owners (field_name, owner_role) VALUES ('Fernando Izo', 'CSA');
REPLACE INTO owners (field_name, owner_role) VALUES ('Sergio Curtale', 'GONE');
REPLACE INTO owners (field_name, owner_role) VALUES ('Ana Naranjo Remesal', 'OTHER');
REPLACE INTO owners (field_name, owner_role) VALUES ('Tania Corrales Sanz', 'OTHER');
REPLACE INTO owners (field_name, owner_role) VALUES ('Silvia Giralda Sato', 'OTHER');


