SELECT eng.engagement_id
FROM engagements eng 
WHERE eng.engagement_partner = "" AND eng.engagement_status > 1 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;