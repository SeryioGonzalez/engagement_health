SELECT eng.engagement_id
FROM engagements eng JOIN owners own ON eng.engagement_owner = own.field_name
WHERE own.owner_role = 'GONE' AND 
INSTR(eng.engagement_name, LOWER('cosell')) = 0;