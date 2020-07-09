SELECT DISTINCT(eng.engagement_id)
FROM milestones mil INNER JOIN engagements eng ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() AND eng.engagement_status < 3
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;
