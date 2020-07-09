SELECT eng.engagement_id
FROM engagements eng JOIN owners own ON eng.engagement_owner = own.field_name
WHERE eng.engagement_status < 4 AND own.owner_role != 'PSS' 
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;
