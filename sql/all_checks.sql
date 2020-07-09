USE pipeline;

#1 - CHECK NAMING CONVENTION PREFIX
SELECT eng.engagement_name
FROM (SELECT engagement_name as engagement_name FROM engagements WHERE INSTR(engagement_name, LOWER('cosell')) = 0) as eng
WHERE SUBSTRING(eng.engagement_name, 1, 8) NOT IN ("FY20_TF_", "FY21_TF_");

#2 - CHECK NAMING CONVENTION ENROLLMENT CODE
DROP VIEW VIEW_ENGAGEMENT_DATA;
CREATE VIEW VIEW_ENGAGEMENT_DATA AS SELECT engagement_name AS engagement_name, SUBSTRING_INDEX(SUBSTRING_INDEX(engagement_name, '_', 3), '_', -1) AS enroll_code
FROM engagements WHERE INSTR(engagement_name, LOWER('cosell')) = 0 AND INSTR(engagement_name, LOWER('FY2')) != 0;
SELECT engagement_name
FROM VIEW_ENGAGEMENT_DATA AS view_eng LEFT JOIN enrollments AS enroll ON view_eng.enroll_code = enroll.enrollment_id 
WHERE enroll.enrollment_id IS NULL;
DROP VIEW VIEW_ENGAGEMENT_DATA;

#### ENGAGEMENT OWNERS ####

#3 - CHECK ENGAGEMENTS NO ACR
SELECT eng.engagement_name 
FROM engagements eng 
WHERE eng.monthly_acr = 0 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#4 - CHECK ENGAGEMENTS NO SPONSOR
SELECT eng.engagement_name 
FROM engagements eng 
WHERE eng.engagement_sponsor = "" AND eng.engagement_status > 1 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#5 - CHECK ENGAGEMENTS NO PARTNER
SELECT eng.engagement_name 
FROM engagements eng 
WHERE eng.engagement_partner = "" AND eng.engagement_status > 1 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#6 - CHECK ENGAGEMENTS OF PHASE CSA
SELECT eng.engagement_name 
FROM engagements eng JOIN owners own ON eng.engagement_owner = own.field_name
WHERE eng.engagement_status > 4 
 AND own.owner_role != 'CSA' 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#7 - CHECK ENGAGEMENTS OF PHASE PSS
SELECT eng.engagement_name
FROM engagements eng JOIN owners own ON eng.engagement_owner = own.field_name
WHERE eng.engagement_status < 4 AND own.owner_role != 'PSS' 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;


#8 - CHECK ENGAGEMENTS OF ANY PHASE NOT IN GONE OWNER
SELECT eng.engagement_name
FROM engagements eng JOIN owners own ON eng.engagement_owner = own.field_name
WHERE own.owner_role = 'GONE' AND 
INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#9 - CHECK ENGAGEMENTS WITH PASSED MILESTONES NOT COMMIT
SELECT DISTINCT(eng.engagement_name)
FROM milestones mil INNER JOIN engagements eng ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() AND eng.engagement_status < 3
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#10 - CHECK MILESTONES NO ACR
SELECT eng.engagement_name
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.monthly_acr = 0 
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#11 - CHECK OLD MILESTONES NOT CLOSED
SELECT eng.engagement_name
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() AND mil.milestone_status NOT IN ("Completed", "Cancelled")
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#12 - CHECK MILESTONES IN THE NEXT 3 MONHTS AND NOT VALIDATE
SELECT eng.engagement_name
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() + INTERVAL 3 MONTH
AND eng.engagement_status < 2
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#13 - CHECK MILESTONES IN THE NEXT 31 DAYS AND NOT COMMIT
SELECT eng.engagement_name
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() + engagementsINTERVAL 31 DAY
AND eng.engagement_status < 2
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;

#14 - CHECK NON MODIFIED ENGAGEMENTS FOR 3 MONTHS
SELECT engagement_name
FROM (SELECT eng.engagement_name, max(mil.milestone_modifiedon_date) AS most_recent_milestone_modified_date, eng.engagement_modified_date
	FROM engagements AS eng LEFT JOIN milestones AS mil ON eng.engagement_id = mil.engagement_id
	WHERE INSTR(eng.engagement_name, LOWER('cosell')) = 0
	GROUP BY eng.engagement_name
) AS engagement_dates
WHERE engagement_dates.engagement_modified_date            < NOW() - INTERVAL 3 MONTH 
	OR engagement_dates.most_recent_milestone_modified_date < NOW() - INTERVAL 3 MONTH 
;

#15 - CHECK ALL MILESTONES GONE
SELECT engagement_name
FROM (SELECT eng.engagement_name, max(mil.milestone_date) AS latest_milestone
	FROM engagements AS eng LEFT JOIN milestones AS mil ON eng.engagement_id = mil.engagement_id
	WHERE INSTR(eng.engagement_name, LOWER('cosell')) = 0
	GROUP BY eng.engagement_name
) AS engagement_date
WHERE engagement_date.latest_milestone < NOW();
