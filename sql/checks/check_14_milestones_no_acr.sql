SELECT eng.engagement_id
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.monthly_acr = 0 
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;
