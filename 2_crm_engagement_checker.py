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

engagement_check_results_file=sys.argv[1]

if engagement_check_results_file == '':
    print("ERROR PROVIDE A FILE FOR STORING RESULTS")
    sys.exit()

with open(engagement_check_results_file, 'w') as outfile:
    json.dump(list_of_checks_and_issues_formatted, outfile)
    
helper_core.log(start_time_seconds, "INFO", "Results stored in {}".format(engagement_check_results_file))

