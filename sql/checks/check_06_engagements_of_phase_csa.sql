SELECT eng.engagement_id
FROM engagements eng JOIN owners own ON eng.engagement_owner = own.field_name
WHERE eng.engagement_status > 3
 AND (own.owner_role != 'CSA' OR own.owner_role IS NULL)
 AND INSTR(eng.engagement_name, LOWER('cosell')) = 0;
