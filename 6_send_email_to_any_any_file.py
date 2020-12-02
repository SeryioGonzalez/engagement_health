import datetime
import helpers.helper_api    as helper_api
import helpers.helper_config as helper_config
import helpers.helper_file   as helper_file
import json
import sys
import time

from helpers.helper_core import Helper

helper_core = Helper()

start_time_seconds = int(round(time.time()))

engagement_check_results_file=sys.argv[1]
if engagement_check_results_file == '':
    print("ERROR PROVIDE A FILE FOR STORING RESULTS")
    sys.exit()
#NOTIFICATION LOGIC
helper_core.log(start_time_seconds, "INFO", "Notifying users according to results in  {}".format(engagement_check_results_file))

teams_notification_endpoint = helper_config.get_config_item('TEAMS', 'TEAMS_NOTIFICATION_API')
teams_channel_email_address = helper_config.get_config_item('TEAMS', 'TEAMS_CHANNEL_EMAIL')
admin_email_address         = helper_config.get_config_item('ADMIN', 'ADMIN_EMAIL')
message_subject_template    = "Telefonica ACR on {}"

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
message_to = [ sys.argv[2] ]

helper_core.log(start_time_seconds, "INFO", "Reading stored in {}".format(engagement_check_results_file))
message_body = '<html><body><br/>'
with open(engagement_check_results_file, 'r') as file:
    data = file.read().replace('\n', '')
message_body += data+'</body></html>'

#CONSTRUCT MESSAGE
message = {'message_subject': message_subject, 'message_body': message_body, 'message_to': message_to}

#SENT IT
helper_core.log(start_time_seconds, "INFO", "Sending notification")
helper_api.post_to_api(teams_notification_endpoint, message)
