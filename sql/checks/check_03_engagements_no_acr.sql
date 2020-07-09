SELECT eng.engagement_id
FROM engagements eng 
WHERE eng.monthly_acr = 0 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;
