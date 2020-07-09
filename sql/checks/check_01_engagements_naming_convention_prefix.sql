SELECT eng.engagement_id
FROM (SELECT engagement_id, engagement_name FROM engagements WHERE INSTR(engagement_name, LOWER('cosell')) = 0) as eng
WHERE SUBSTRING(eng.engagement_name, 1, 8) NOT IN ("FY20_TF_", "FY21_TF_");
