SELECT eng.engagement_id
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() + INTERVAL 3 MONTH
AND eng.engagement_status < 2
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;