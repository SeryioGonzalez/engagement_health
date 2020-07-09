
import pymysql.cursors
import datetime
import helpers.helper_config as helper_config

sql_insert_statement_template_milestone  = "REPLACE INTO {SQL_TABLE} (milestone_id, milestone_name, engagement_id, monthly_acr, milestone_date, milestone_status, milestone_modifiedon_date) VALUES ('{MILESTONE_ID}', '{MILESTONE_NAME}', '{ENGAGEMENT_ID}', {MONTHLY_ACR}, '{MILESTONE_DATE}', '{MILESTONE_STATUS}', '{MILESTONE_MODIFIED_DATE}' ) "
sql_insert_statement_template_engagement = "REPLACE INTO {SQL_TABLE} (engagement_id, engagement_name, monthly_acr, engagement_status, engagement_owner, engagement_completion_date, engagement_sponsor, engagement_partner, engagement_state, engagement_preferred_region, engagement_start_date, engagement_created_date, engagement_modified_date, engagement_status_label, engagement_workload, engagement_solution_area, engagement_health_label, engagement_account_id, msp_engagementid) VALUES ('{ENGAGEMENT_ID}', '{ENGAGEMENT_NAME}', {ENGAGEMENT_ACR}, {ENGAGEMENT_STAGE}, '{ENGAGEMENT_OWNER}', '{ENGAGEMENT_COMPLETION_DATE}', '{ENGAGEMENT_SPONSOR}', '{ENGAGEMENT_PARTNER}', '{ENGAGEMENT_STATE}', '{ENGAGEMENT_PREFERRED_REGION}', '{ENGAGEMENT_START_DATE}', '{ENGAGEMENT_CREATED_DATE}', '{ENGAGEMENT_MODIFIED_DATE}','{ENGAGEMENT_STATUS_LABEL}', '{ENGAGEMENT_WORKLOAD}', '{ENGAGEMENT_SOLUTION_AREA}', '{ENGAGEMENT_HEALTH_LABEL}', '{ENGAGEMENT_ACCOUNT_ID}', '{MSP_ENGAGEMENT_ID}' ) "

sql_select_statement_template_field_name_from_field_id = "SELECT field_name FROM {SQL_TABLE} WHERE field_id = '{FIELD_ID}'"
sql_insert_statement_template_field_name_from_field_id = "REPLACE INTO {SQL_TABLE} (field_id, field_name) VALUES ('{FIELD_ID}', '{FIELD_NAME}')"

sql_engagement_info_select_statement_template = "SELECT engagement_name, engagement_owner, engagement_status FROM engagements WHERE engagement_name = '{}'"

sql_engagement_all_info_select_statement_template = "SELECT * FROM engagements WHERE engagement_id= '{}'"

def execute_insert_query_list(database_connection, query_list):
     
    for query in query_list:
        _execute_query(database_connection, query)

def _execute_query(database_connection, query):
    database_cursor = database_connection.cursor()
    clean_query = query.strip()
    database_cursor.execute(clean_query)
    database_connection.commit()

    query_result = database_cursor.fetchall()

    return query_result

def execute_select_query(database_connection, sql_select_statement):
    return _execute_query(database_connection, sql_select_statement)


def get_engagement_data(database_connection, engagement_name):
    sql_engagement_info_select_statement = sql_engagement_info_select_statement_template.format(engagement_name)
    query_result = _execute_query(database_connection, sql_engagement_info_select_statement)
    
    return query_result

def get_engagement_all_data(database_connection, engagement_id):
    sql_engagement_all_info_select_statement = sql_engagement_all_info_select_statement_template.format(engagement_id)
    query_result = _execute_query(database_connection, sql_engagement_all_info_select_statement)[0]
    
    for key in query_result.keys():
        if type(query_result[key]) == datetime.datetime:
            query_result[key] = query_result[key].strftime("%Y-%m-%d")
            
    return query_result

def execute_query_file(database_connection, sql_query_file):

    with open(sql_query_file) as sql_file:
        sql_as_string_list = sql_file.read().split(';')
        sql_as_string_list.pop()

        database_cursor = database_connection.cursor()

        for sql_as_string in sql_as_string_list:
            database_cursor.execute(sql_as_string + ";")
            query_result = database_cursor.fetchall()
        
        if type(query_result) is tuple and len(query_result) == 0:
            return None
        else:    
            return query_result

def get_database_connection():
    #GET DATABASE CONNECTION DATA
    sql_database_server = helper_config.get_config_item("SQL", "DATABASE_SERVER")
    sql_database_name   = helper_config.get_config_item("SQL", "DATABASE_NAME")
    sql_database_user   = helper_config.get_config_item("SQL", "DATABASE_USER")
    sql_database_pass   = helper_config.get_config_item("SQL", "DATABASE_PASS")

    database_connection = pymysql.connect(host=sql_database_server, user=sql_database_user, password=sql_database_pass, db=sql_database_name,  cursorclass=pymysql.cursors.DictCursor)
    
    return database_connection

def get_milestone_sql_insert_statement(milestone_table, milestone_dict_data):

    milestones_sql_insert_parameters = {}
    milestones_sql_insert_parameters['SQL_TABLE']                = milestone_table
    milestones_sql_insert_parameters['MILESTONE_ID']             = milestone_dict_data['msp_milestonenumber']
    milestones_sql_insert_parameters['MILESTONE_NAME']           = milestone_dict_data['msp_name']
    milestones_sql_insert_parameters['ENGAGEMENT_ID']            = milestone_dict_data['msp_uatengagementnumber']
    milestones_sql_insert_parameters['MONTHLY_ACR']              = _normalize_integers(milestone_dict_data['msp_monthlyuse'])
    milestones_sql_insert_parameters['MILESTONE_MODIFIED_DATE'] = milestone_dict_data['modifiedon']
    milestones_sql_insert_parameters['MILESTONE_DATE']           = milestone_dict_data['msp_milestonedate']
    milestones_sql_insert_parameters['MILESTONE_STATUS']         = milestone_dict_data['_msp_milestonestatus_label']

    milestone_sql_insert_statement = sql_insert_statement_template_milestone.format(**milestones_sql_insert_parameters)

    return milestone_sql_insert_statement 

def get_engagement_sql_insert_statement(engagement_table, engagement_dict_data):

    engagements_sql_insert_parameters = {}
    engagements_sql_insert_parameters['SQL_TABLE']                  = engagement_table
    engagements_sql_insert_parameters['ENGAGEMENT_ID']              = engagement_dict_data['msp_engagementnumber']
    engagements_sql_insert_parameters['ENGAGEMENT_NAME']            = engagement_dict_data['msp_name']
    engagements_sql_insert_parameters['ENGAGEMENT_STAGE']           = engagement_dict_data['engagement_status']
    engagements_sql_insert_parameters['ENGAGEMENT_ACR']             = _normalize_integers(engagement_dict_data['msp_rollupestrevenue_base'])
    engagements_sql_insert_parameters['ENGAGEMENT_OWNER']           = engagement_dict_data['_ownerid_value']
    engagements_sql_insert_parameters['ENGAGEMENT_COMPLETION_DATE'] = engagement_dict_data['msp_estcompletiondate']
    engagements_sql_insert_parameters['ENGAGEMENT_SPONSOR']         = engagement_dict_data['_msp_contactid_value']
    engagements_sql_insert_parameters['ENGAGEMENT_PARTNER']         = engagement_dict_data['_msp_partneraccountid_value']
    
    engagements_sql_insert_parameters['ENGAGEMENT_STATE']            = engagement_dict_data['statecode']
    engagements_sql_insert_parameters['ENGAGEMENT_PREFERRED_REGION'] = engagement_dict_data['_msp_preferredazureregion_label']
    engagements_sql_insert_parameters['ENGAGEMENT_START_DATE']       = engagement_dict_data['msp_eststartdate']
    engagements_sql_insert_parameters['ENGAGEMENT_CREATED_DATE']     = engagement_dict_data['createdon']
    engagements_sql_insert_parameters['ENGAGEMENT_STATUS_LABEL']     = engagement_dict_data['_msp_engagementstatus_label']
    engagements_sql_insert_parameters['ENGAGEMENT_WORKLOAD']         = engagement_dict_data['_msp_workloadtype_label']
    engagements_sql_insert_parameters['ENGAGEMENT_MODIFIED_DATE']    = engagement_dict_data['modifiedon']
    engagements_sql_insert_parameters['ENGAGEMENT_SOLUTION_AREA']    = engagement_dict_data['_msp_solutionarea_label']
    engagements_sql_insert_parameters['ENGAGEMENT_HEALTH_LABEL']     = engagement_dict_data['_msp_engagementhealth_label']
    engagements_sql_insert_parameters['ENGAGEMENT_ACCOUNT_ID']       = engagement_dict_data['_msp_accountid_value']
    engagements_sql_insert_parameters['MSP_ENGAGEMENT_ID']           = engagement_dict_data['msp_engagementid']

    engagement_sql_insert_statement = sql_insert_statement_template_engagement.format(**engagements_sql_insert_parameters)

    return engagement_sql_insert_statement 

def map_field_id_to_name_in_db_table(database_connection, field_id, database_table):
    
    field_name = ''

    #PERFORM AND SQL CHECK
    sql_statement = sql_select_statement_template_field_name_from_field_id.format(SQL_TABLE = database_table, FIELD_ID = field_id)
    query_result = _execute_query(database_connection, sql_statement)
    
    if type(query_result) is not tuple:
        field_name = query_result[0]['field_name']
    else:
        return None

    return field_name

def _normalize_integers(int_string):
    if int_string in (None, "None", "NULL"):
        return "NULL"
    else:
        return int(int_string)

def update_field_name_for_field_id(database_connection, database_table, field_id, field_name):
    sql_insert_statement_template_field_name_from_field_id

    sql_statement = sql_insert_statement_template_field_name_from_field_id.format(SQL_TABLE = database_table, FIELD_ID = field_id, FIELD_NAME = field_name)
    query_result = _execute_query(database_connection, sql_statement)