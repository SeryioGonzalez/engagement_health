import helpers.helper_api    as helper_api
import helpers.helper_config as helper_config
import helpers.helper_file   as helper_file
import helpers.helper_sql    as helper_sql
import json
import os
import time

class Helper:

    def __init__(self):
        self.database_connection = helper_sql.get_database_connection()

    def get_milestone_sql_insert_statement(self, milestones_sql_table, milestone_dict_data):
        return helper_sql.get_milestone_sql_insert_statement(milestones_sql_table, milestone_dict_data)

    def get_engagement_sql_insert_statement(self, engagements_sql_table, engagement_dict_data):
        return helper_sql.get_engagement_sql_insert_statement(engagements_sql_table, engagement_dict_data)

    def _get_engagement_all_data(self, engagement_id):
        return helper_sql.get_engagement_all_data(self.database_connection, engagement_id)

    def execute_insert_query_list(self, sql_insert_statements ):
        helper_sql.execute_insert_query_list(self.database_connection, sql_insert_statements )

    def execute_select_query(self, sql_select_statement ):
        return helper_sql.execute_select_query(self.database_connection, sql_select_statement)

    def get_owner_emails(self, engagement_owner_names):
        query = 'SELECT owner_mail FROM owners WHERE field_name IN {}'.format(list(engagement_owner_names)).replace("[","(").replace("]",")")
        owner_email_results = self.execute_select_query(query)
        owner_emails = [owner_email_result['owner_mail'] for owner_email_result in owner_email_results]

        return owner_emails

    def execute_query_file(self, sql_query_file ):
        return helper_sql.execute_query_file(self.database_connection, sql_query_file )

    def log(self, start_time_seconds, log_level, message):
        time_seconds_now = int(round(time.time()))
        time_seconds = time_seconds_now - start_time_seconds

        print("{:04} - {}".format(time_seconds, message))

    def map_owner_id_to_name(self, owner_id_set):
        
        owner_db  = helper_config.get_config_item("SQL",  "DATABASE_TABLE_FOR_OWNERS")
        owner_api = helper_config.get_config_item("API", "URL_MAP_OWNER")
        owner_in_crm_data_model  = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS",  "CRM_OWNER_NAME")

        return self._map_field_ids (owner_id_set, owner_db, owner_api, owner_in_crm_data_model)

    def map_sponsor_id_to_name(self, field_id_set):
        
        field_db  = helper_config.get_config_item("SQL",  "DATABASE_TABLE_FOR_SPONSORS")
        field_api = helper_config.get_config_item("API", "URL_MAP_SPONSOR")
        field_in_crm_data_model  = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS",  "CRM_SPONSOR_NAME")

        return self._map_field_ids (field_id_set, field_db, field_api, field_in_crm_data_model)

    def map_partner_id_to_name(self, field_id_set):
        
        field_db_table  = helper_config.get_config_item("SQL",  "DATABASE_TABLE_FOR_PARTNERS")
        field_api = helper_config.get_config_item("API", "URL_MAP_PARTNER")
        field_in_crm_data_model  = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS",  "CRM_PARTNER_NAME")
        
        return self._map_field_ids (field_id_set, field_db_table, field_api, field_in_crm_data_model)

    def _map_field_ids(self, field_id_set, field_database_table, field_api_url, field_in_crm_data_model):
        
        mappings = {}

        for field_id in field_id_set:
            field_name = ''

            #IT CAN BE A NULL TERM
            if field_id == "NULL":
                field_name == "NULL"
            else:
                #TRY AN SQL CHECK
                field_name_sql_result = helper_sql.map_field_id_to_name_in_db_table(self.database_connection, field_id, field_database_table)
                
                if field_name_sql_result == None:
                    #TRY THEN AN API CHECK
                    field_name_api_result = helper_api.map_field_id_to_name_in_api(field_id, field_api_url, field_in_crm_data_model)
                    field_name = field_name_api_result

                    #STORA DATA IN SQL FOR FUTURE USAGE
                    helper_sql.update_field_name_for_field_id(self.database_connection, field_database_table, field_id, field_name)

                else:
                    field_name = field_name_sql_result
            
            mappings[field_id] = field_name
        
        return mappings

    def translate_mappings_from_dict(self, item_list, crm_field, field_id_to_name_mapping):
        modified_item_list = []

        for item in item_list:
            #COPY ITEM TO MODIFIED VALUE        
            modified_item = item
            #FIND ELEMENT IN ITEM DICTIONARY
            item_id_value = item[crm_field]
            
            #REPLACE VALUE IN MODIFIED ITEM
            modified_item[crm_field] = field_id_to_name_mapping[item_id_value]
        
            #APPEND ITEM TO LIST
            modified_item_list.append(modified_item)

        return modified_item_list

    def get_check_description_in_file(self, sql_check_file):
        head, tail = os.path.split(sql_check_file)
        
        file_data = tail[0:-4]
        check_num  = int(file_data.split('_')[1])
        check_type = file_data.split('_')[2].capitalize() 
        check_description = " ".join(file_data.split('_')[3:]).capitalize() 

        return check_num, check_type, check_description

    def get_check_id_in_file(self, sql_check_file):
        head, tail = os.path.split(sql_check_file)
        
        file_data = tail[0:-4]
        check_num  = int(file_data.split('_')[1])
        
        return check_num

    def get_engagement_info(self, engagement_data):
        engagement_name = engagement_data['engagement_name']
        engagement_info = helper_sql.get_engagement_data(self.database_connection, engagement_name)

        return engagement_info[0]

    def format_result(self, result_data):

        affected_engagement_id_list = result_data[3]  
        affected_engagement_data_list = [self._format_engagement(engagement_id) for engagement_id in affected_engagement_id_list]

        result_dict = {
            'check_id': result_data[0],
            'check_type': result_data[1],
            'check_description': result_data[2],
            'affected_items': affected_engagement_data_list
        }

        return result_dict

    def _format_engagement(self, engagement_id):
        if engagement_id is None:
            return None

        engagement_data = self._get_engagement_all_data(engagement_id)
        return  engagement_data 

    def insert_bpf_field_to_engagements(self, filtered_engagement_list):
        #SELECT BPF TRANSLATION API
        
        crm_engagement_id_field        = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_ENGAGEMENT_ID_FIELD")
        crm_engagement_id_in_bpf_field = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_BPF_ENGAGEMENT_ID_FIELD")
        local_engagement_status_field  = helper_config.get_config_item("LOCAL_DATA_MODEL_FIELDS", "ENGAGEMENT_STATUS_FIELD")

        #LIST WITH THE ENGAGEMENTS WITH THE BPF FIELD
        bpf_mapped_engagements = []

        engagement_ids = [ filtered_engagement[crm_engagement_id_field] for filtered_engagement in filtered_engagement_list ]
        engagement_id_to_bpf_status_dict = helper_api.translate_bpfs_to_status(engagement_ids)

        for filtered_engagement in filtered_engagement_list:
            engagement_status = [bpf_status for bpf_status in engagement_id_to_bpf_status_dict if bpf_status[crm_engagement_id_in_bpf_field] == filtered_engagement[crm_engagement_id_field]][0][local_engagement_status_field]
            filtered_engagement[local_engagement_status_field] = engagement_status
            bpf_mapped_engagements.append(filtered_engagement)

        return bpf_mapped_engagements