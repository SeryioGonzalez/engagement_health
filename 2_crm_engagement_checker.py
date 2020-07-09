import helpers.helper_api    as helper_api
import helpers.helper_config as helper_config
import helpers.helper_file   as helper_file
import json
import time
import datetime
from helpers.helper_core import Helper

helper_core = Helper()

start_time_seconds = int(round(time.time()))
helper_core.log(start_time_seconds, "INFO", "Starting program")

engagement_check_folder  = helper_config.get_config_item("SQL", "CHECK_SCRIPT_FOLDER")
sql_check_files = helper_file.get_file_paths_in_folder(engagement_check_folder )

helper_core.log(start_time_seconds, "INFO", "Starting SQL checks")
list_of_checks_and_issues = []

for sql_check_file in sql_check_files:
    check_id, check_type, check_description = helper_core.get_check_description_in_file(sql_check_file)
    query_result = helper_core.execute_query_file(sql_check_file)
    
    engagement_id_list = []
    if query_result is not None:
        engagement_id_list = [ engagement_data['engagement_id'] for engagement_data in query_result ]

    engagement_check_data = (check_id, check_type, check_description, engagement_id_list )

    list_of_checks_and_issues.insert(check_id, engagement_check_data)

helper_core.log(start_time_seconds, "INFO", "Check data collected")

helper_core.log(start_time_seconds, "INFO", "Model response")
list_of_checks_and_issues_formatted = [helper_core.format_result(check_result) for check_result in list_of_checks_and_issues]

helper_core.log(start_time_seconds, "INFO", "Store results in file")
engagement_check_results_folder  = helper_config.get_config_item("FILES", "CHECK_RESULT_FOLDER")
engagement_check_results_filename_template  = helper_config.get_config_item("FILES", "CHECK_RESULT_FILENAME_TEMPLATE")
now_string = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
engagement_check_results_file = engagement_check_results_folder + engagement_check_results_filename_template.format(now_string)

with open(engagement_check_results_file, 'w') as outfile:
    json.dump(list_of_checks_and_issues_formatted, outfile)
    
helper_core.log(start_time_seconds, "INFO", "Results stored in {}".format(engagement_check_results_file))

#NOTIFICATION LOGIC
helper_core.log(start_time_seconds, "INFO", "Notifying users according to results in  {}".format(engagement_check_results_file))

teams_notification_endpoint = helper_config.get_config_item('TEAMS', 'TEAMS_NOTIFICATION_API')
teams_channel_email_address = helper_config.get_config_item('TEAMS', 'TEAMS_CHANNEL_EMAIL')
admin_email_address         = helper_config.get_config_item('ADMIN', 'ADMIN_EMAIL')
message_subject_template    = helper_config.get_config_item('TEAMS', 'TEAMS_MESSAGE_SUBJECT_TEMPLATE')

engagement_crm_link_template = helper_config.get_config_item('CRM_DATA_MODEL_FIELDS', 'CRM_ENGAGEMENT_LINK_TEMPLATE')

#The order of engagement_name second and msp_engagementid last must be kept
engagement_keys_of_interest = [
    'engagement_owner',
    'engagement_name',
    'engagement_status',
    'engagement_sponsor',
    'engagement_partner',
    'engagement_start_date',
    'msp_engagementid'
]

message_subject = message_subject_template.format( datetime.date.today())
message_to = [ teams_channel_email_address, admin_email_address ]

message_body = '<html><body><br/>'
helper_core.log(start_time_seconds, "INFO", "Reading stored in {}".format(engagement_check_results_file))
with open(engagement_check_results_file) as fp:
    results_data = json.load(fp)
    if len(results_data) > 0:
        helper_core.log(start_time_seconds, "INFO", "Items to correct: {}".format(len(results_data)))
        for result in results_data:
            if len(result['affected_items']) > 0:
                #AFFECTED CHECK INFO
                check_title = "<h1><b>Check {:02d}: {} - {}</b></h1>".format(result['check_id'], result['check_type'], result['check_description'])
                
                #SELECT FIELDS OF INTEREST IN AFFECTED ENGAGEMENTS
                result_affected_items_all_data = result['affected_items']
                result_affected_items_filtered_data = [ { dict_key_of_interest: result_affected_item_all_data[dict_key_of_interest] for dict_key_of_interest in engagement_keys_of_interest } for result_affected_item_all_data in result_affected_items_all_data ]

                check_table = '<table>'
                #Remove redundant info in field name
                engagement_keys_of_interest_filtered = [  one_key.replace("engagement_", "").upper() for one_key in engagement_keys_of_interest   ]
                #Remove the last field
                engagement_keys_of_interest_filtered.pop()
                check_table_header = '<tr><th>' + '</th><th>'.join(engagement_keys_of_interest_filtered) + '</th></tr>'

                check_table_rows = []
                for filtered_engagement in result_affected_items_filtered_data:
                    filtered_engagement_values = [  str(filtered_engagement[key_of_interest]) for key_of_interest in engagement_keys_of_interest ]

                    #The last value 'msp_engagementid' is just for creating a link
                    msp_engagementid = filtered_engagement_values.pop()
                    engagement_crm_link = engagement_crm_link_template.format(msp_engagementid)
                    
                    filtered_engagement_values[1] = '<a href="{}">{}</a>'.format(engagement_crm_link,  filtered_engagement_values[1])

                    check_table_row = '<tr><td>' + '</td><td>'.join(filtered_engagement_values) + '</td></tr>'
                    check_table_rows.append(check_table_row)

                check_table += check_table_header
                for check_table_row in check_table_rows:
                    check_table += check_table_row
                
                check_table += '</table><br/>'

                message_body += check_title
                message_body += check_table
        
        #Take emails from owners
        engagement_owner_names = set()
        for result in results_data:
            [engagement_owner_names.add(affected_item['engagement_owner']) for affected_item in result['affected_items']]
        
        engagement_owner_emails = helper_core.get_owner_emails(engagement_owner_names)

        [message_to.append(email) for email in engagement_owner_emails]
        
    else:
        helper_core.log(start_time_seconds, "INFO", "No items to correct")
        message_body = '<h1> No affected items today</h1>'    

#CLOSE HTML AND INSERT STYLE
message_body += '</body></html>'
message_body = message_body.replace('<table>', '<table style="border: 1px solid black; text-align: center; padding:2px; ">')
message_body = message_body.replace('<th>',    '<th    style="border: 1px solid black; text-align: center; padding:2px; ">')
message_body = message_body.replace('<td>',    '<td    style="border: 1px solid black; text-align: center; padding:2px; ">')

#CONSTRUCT MESSAGE
message = {'message_subject': message_subject, 'message_body': message_body, 'message_to': message_to}

#SENT IT
helper_core.log(start_time_seconds, "INFO", "Sending notification")
helper_api.post_to_api(teams_notification_endpoint, message)
