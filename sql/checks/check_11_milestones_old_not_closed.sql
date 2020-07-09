SELECT eng.engagement_id
FROM engagements eng INNER JOIN milestones mil ON eng.engagement_id = mil.engagement_id
WHERE mil.milestone_date < NOW() AND mil.milestone_status NOT IN ("Completed", "Cancelled")
AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;
