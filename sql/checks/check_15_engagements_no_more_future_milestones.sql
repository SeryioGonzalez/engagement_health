SELECT engagement_id
FROM (SELECT eng.engagement_id, max(mil.milestone_date) AS milestone_date
	FROM engagements AS eng LEFT JOIN milestones AS mil ON eng.engagement_id = mil.engagement_id
	WHERE INSTR(eng.engagement_name, LOWER('cosell')) = 0
	GROUP BY eng.engagement_id
) AS engagement_dates
WHERE milestone_date <  NOW();
