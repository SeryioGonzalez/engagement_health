CREATE VIEW VIEW_ENGAGEMENT_DATA AS SELECT engagement_id AS engagement_id, SUBSTRING_INDEX(SUBSTRING_INDEX(engagement_name, '_', 3), '_', -1) AS enroll_code
FROM engagements WHERE INSTR(engagement_name, LOWER('cosell')) = 0 AND INSTR(engagement_name, LOWER('FY2')) != 0;
SELECT engagement_id
FROM VIEW_ENGAGEMENT_DATA AS view_eng LEFT JOIN enrollments AS enroll ON view_eng.enroll_code = enroll.enrollment_id 
WHERE enroll.enrollment_id IS NULL;

DROP VIEW VIEW_ENGAGEMENT_DATA;