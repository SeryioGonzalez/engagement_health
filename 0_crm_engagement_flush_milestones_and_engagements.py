import helpers.helper_api    as helper_api
import helpers.helper_config as helper_config
import helpers.helper_file   as helper_file
import time
from helpers.helper_core import Helper

helper_core = Helper()

start_time_seconds = int(round(time.time()))
helper_core.log(start_time_seconds, "INFO", "Starting program")

helper_core.log(start_time_seconds, "INFO", 'Execute milestones truncate query')
milestones_sql_truncate_statement = helper_config.get_config_item("SQL", "DATABASE_MILESTONES_TRUNCATE_STATEMENT")
helper_core.execute_query_file(milestones_sql_truncate_statement )    

helper_core.log(start_time_seconds, "INFO", 'Execute engagements truncate query')
engagements_sql_truncate_statement = helper_config.get_config_item("SQL", "DATABASE_ENGAGEMENTS_TRUNCATE_STATEMENT")
helper_core.execute_query_file(engagements_sql_truncate_statement )  

helper_core.log(start_time_seconds, "INFO", 'Done')