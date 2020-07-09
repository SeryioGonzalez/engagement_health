SELECT engagement_id
FROM (SELECT eng.engagement_id, max(mil.milestone_modifiedon_date) AS most_recent_milestone_modified_date, eng.engagement_modified_date
	FROM engagements AS eng LEFT JOIN milestones AS mil ON eng.engagement_id = mil.engagement_id
	WHERE INSTR(eng.engagement_name, LOWER('cosell')) = 0
	GROUP BY eng.engagement_id
) AS engagement_dates
WHERE engagement_dates.engagement_modified_date            <  NOW() - INTERVAL 3 MONTH 
	OR engagement_dates.most_recent_milestone_modified_date < NOW() - INTERVAL 3 MONTH 
;
