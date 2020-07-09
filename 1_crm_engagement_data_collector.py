import helpers.helper_api    as helper_api
import helpers.helper_config as helper_config
import helpers.helper_file   as helper_file
import time
from helpers.helper_core import Helper

helper_core = Helper()

start_time_seconds = int(round(time.time()))
helper_core.log(start_time_seconds, "INFO", "Starting program")

engagement_keys_of_interest = ['statecode', '_msp_preferredazureregion_label', 'msp_eststartdate', 'createdon', '_msp_engagementstatus_label', '_msp_workloadtype_label', 'modifiedon', '_msp_solutionarea_label', '_msp_engagementhealth_label', 'msp_estcompletiondate', '_msp_accountid_value', 'msp_engagementnumber', 'msp_engagementid', 'msp_name', 'msp_rollupestrevenue_base', '_ownerid_value', 'msp_estcompletiondate', '_msp_contactid_value', '_msp_partneraccountid_value']
milestone_keys_of_interest  = ['msp_uatengagementnumber', 'msp_milestonenumber', 'msp_name', 'modifiedon', 'msp_milestonedate', '_msp_milestonestatus_label', 'msp_monthlyuse']

engagement_collection_api_url = helper_config.get_config_item("API",  "URL_ALL_ENGAGEMENTS")
engagement_raw_data_file      = helper_config.get_config_item("FILES", "ENGAGEMENT_RAW_DATA")
engagement_filtered_data_file = helper_config.get_config_item("FILES", "ENGAGEMENT_FILTERED_DATA")
engagement_mapped_data_file   = helper_config.get_config_item("FILES", "ENGAGEMENT_MAPPED_DATA")

milestone_collection_api_url  = helper_config.get_config_item("API",  "URL_ALL_MILESTONES")
milestone_raw_data_file      = helper_config.get_config_item("FILES", "MILESTONE_RAW_DATA")
milestone_filtered_data_file  = helper_config.get_config_item("FILES", "MILESTONE_FILTERED_DATA")

############## 1 #################

helper_core.log(start_time_seconds, "INFO", "Calling milestones API")
raw_data_milestones = helper_api.get_json_from_collection_api(milestone_collection_api_url)

helper_core.log(start_time_seconds, "INFO", "Storing milestone raw data")
helper_file.write_list_to_file_in_json(raw_data_milestones, milestone_raw_data_file )

helper_core.log(start_time_seconds, "INFO", "Filtering milestone data")
filtered_milestone_items = helper_api.filter_data_items(raw_data_milestones, milestone_keys_of_interest)

helper_core.log(start_time_seconds, "INFO", "Storing milestone data")
helper_file.write_list_to_file_in_json(filtered_milestone_items, milestone_filtered_data_file )

helper_core.log(start_time_seconds, "INFO", "Calling engagements API")
raw_data_engagements = helper_api.get_json_from_collection_api(engagement_collection_api_url)

helper_core.log(start_time_seconds, "INFO", "Storing engagement raw data")
helper_file.write_list_to_file_in_json(raw_data_engagements, engagement_raw_data_file )

helper_core.log(start_time_seconds, "INFO", "Filtering engagement data")
filtered_engagement_items = helper_api.filter_data_items(raw_data_engagements, engagement_keys_of_interest)

helper_core.log(start_time_seconds, "INFO", "Storing engagement data")
helper_file.write_list_to_file_in_json(filtered_engagement_items, engagement_filtered_data_file )

############## PROCESS ENGAGEMENTS #################

#SELECT UNMAPPED FIELDS OF INTERES
crm_engagement_owner_field   = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_ENGAGEMENT_OWNER_FIELD")
crm_engagement_sponsor_field = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_ENGAGEMENT_SPONSOR_FIELD")
crm_engagement_partner_field = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_ENGAGEMENT_PARTNER_FIELD")

#READ FILE WITH FILTERED DATA BUT UNMAPPED FIELDS
filtered_engagements = helper_file.read_lines_as_list_from_json_file(engagement_filtered_data_file)

#ADD BPF STATUS
helper_core.log(start_time_seconds, "INFO", "Adding BPF status in engagements")
mapped_engagements = helper_core.insert_bpf_field_to_engagements(filtered_engagements)

#GET OWNER ID LIST
helper_core.log(start_time_seconds, "INFO", "Mapping owner data in engagements")
owner_id_set_in_engagements = set( filtered_engagement[crm_engagement_owner_field ] for filtered_engagement in mapped_engagements )
owner_id_to_name_mapping = helper_core.map_owner_id_to_name(owner_id_set_in_engagements)
mapped_engagements = helper_core.translate_mappings_from_dict(mapped_engagements, crm_engagement_owner_field, owner_id_to_name_mapping)

#GET SPONSOR ID LIST
helper_core.log(start_time_seconds, "INFO", "Mapping sponsor data in engagements")
sponsor_id_set_in_engagements = set( filtered_engagement[crm_engagement_sponsor_field] for filtered_engagement in mapped_engagements )
sponsor_id_to_name_mapping = helper_core.map_sponsor_id_to_name(sponsor_id_set_in_engagements)
mapped_engagements = helper_core.translate_mappings_from_dict(mapped_engagements, crm_engagement_sponsor_field, sponsor_id_to_name_mapping)

#GET PARTNER ID LIST
helper_core.log(start_time_seconds, "INFO", "Mapping partner data in engagements")
partner_id_set_in_engagements = set( filtered_engagement[crm_engagement_partner_field] for filtered_engagement in mapped_engagements )
partner_id_to_name_mapping = helper_core.map_partner_id_to_name(partner_id_set_in_engagements)
mapped_engagements = helper_core.translate_mappings_from_dict(mapped_engagements, crm_engagement_partner_field, partner_id_to_name_mapping)

#STORING DATA TO FILE
helper_core.log(start_time_seconds, "INFO", "Storing engagements mapped data")
helper_file.write_list_to_file_in_json(mapped_engagements, engagement_mapped_data_file )
############## 4 #################

milestones_json_file = helper_config.get_config_item("FILES",  "MILESTONE_FILTERED_DATA")
milestones_sql_table = helper_config.get_config_item("SQL",   "DATABASE_TABLE_FOR_MILESTONES")
milestones_sql_insert_statements_file = helper_config.get_config_item("SQL", "DATABASE_MILESTONES_INSERT_STATEMENTS")

engagements_json_file=helper_config.get_config_item("FILES", "ENGAGEMENT_MAPPED_DATA")
engagements_sql_table=helper_config.get_config_item("SQL",   "DATABASE_TABLE_FOR_ENGAGEMENTS")
engagements_sql_insert_statements_file = helper_config.get_config_item("SQL", "DATABASE_ENGAGEMENTS_INSERT_STATEMENTS")

helper_core.log(start_time_seconds, "INFO", "Generate SQL statements for engagements")
engagements_sql_insert_statements = [ helper_core.get_engagement_sql_insert_statement(engagements_sql_table, engagement_dict_data) for engagement_dict_data in  helper_file.read_json_file(engagements_json_file)]

helper_core.log(start_time_seconds, "INFO", "Store SQL statements for engagements in file")
helper_file.write_list_to_file(engagements_sql_insert_statements, engagements_sql_insert_statements_file)

helper_core.log(start_time_seconds, "INFO", "Generate SQL statements for milestones")
milestones_sql_insert_statements = [ helper_core.get_milestone_sql_insert_statement(milestones_sql_table, milestone_dict_data)     for milestone_dict_data  in  helper_file.read_json_file(milestones_json_file)]

helper_core.log(start_time_seconds, "INFO", "Store SQL statements for milestones in file")
helper_file.write_list_to_file(milestones_sql_insert_statements,  milestones_sql_insert_statements_file)

############## 5 #################

#SELECT SQL QUERY FILES
milestones_sql_insert_statements_file  = helper_config.get_config_item("SQL", "DATABASE_MILESTONES_INSERT_STATEMENTS")
engagements_sql_insert_statements_file = helper_config.get_config_item("SQL", "DATABASE_ENGAGEMENTS_INSERT_STATEMENTS")

#RETRIEVE QUERY LIST FROM FILES AND INSERT IT
helper_core.log(start_time_seconds, "INFO", 'Execute milestones insert queries')
milestones_sql_insert_statements  = helper_file.read_lines_as_list_from_file(milestones_sql_insert_statements_file)
helper_core.execute_insert_query_list(milestones_sql_insert_statements )    

helper_core.log(start_time_seconds, "INFO", 'Execute engagements insert queries')
engagements_sql_insert_statements = helper_file.read_lines_as_list_from_file(engagements_sql_insert_statements_file)
helper_core.execute_insert_query_list(engagements_sql_insert_statements)

helper_core.log(start_time_seconds, "INFO", 'Done')