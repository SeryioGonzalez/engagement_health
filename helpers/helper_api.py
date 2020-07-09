import json
import helpers.helper_config as helper_config
import requests

crm_engagement_id_in_bpf_field = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_BPF_ENGAGEMENT_ID_FIELD")
bpf_status_field        = helper_config.get_config_item("CRM_DATA_MODEL_FIELDS", "CRM_BPF_STATUS_FIELD")
engagement_status_field = helper_config.get_config_item('LOCAL_DATA_MODEL_FIELDS', 'ENGAGEMENT_STATUS_FIELD')

engagement_bpf_status_id_to_number = {
    '8e2f31db-bb99-4dea-bd35-e9a82c5a8f70' : 1,
    '6d4ca41e-66ce-943d-2223-923a6a60b862' : 2,
    '34628c28-b271-42c1-b166-4ff93f8bf09c' : 3,
    '10567144-e2e6-d9b1-0deb-81c2c3bd5c56' : 4,
    '109d1d5b-beaa-d7d3-4929-2184cae5c39b' : 5
}

bpf_keys_of_interest = [crm_engagement_id_in_bpf_field , bpf_status_field]

def get_json_from_collection_api(api_endpoint):
    raw_data_items = _query_api(api_endpoint)

    return raw_data_items

def map_field_id_to_name_in_api(field_id, api_endpoint, field_in_crm_data_model):
    post_body = {'element_id': field_id}
    response_object = _query_api(api_endpoint, post_body)

    field_name = response_object[0][field_in_crm_data_model]

    return field_name

def post_to_api(api_endpoint, post_body):
    _post_to_api(api_endpoint, post_body)

def map_filter_query_in_api(filter_query, api_endpoint):
    post_body = {'filter_query': filter_query}
    response_object = _query_api(api_endpoint, post_body)
    fields = response_object

    return fields

def _post_to_api(api_endpoint, post_body):
    headers = {'Content-type': 'application/json'}
    response = requests.post(api_endpoint, json = post_body, headers=headers)


def _query_api(api_endpoint, post_body = None):
    headers = {'Content-type': 'application/json'}

    if post_body is None:
        post_body = {"kind": "Http", "inputs": {"schema": {}}}

    response = requests.post(api_endpoint, json = post_body, headers=headers)
    response_json = response.json()

    response_object = response_json['value']

    return response_object

def filter_data_items(raw_data_items, item_keys_of_interest):
    filtered_data_items = []
    #Iterate over every retrieved object
    for raw_data_item in raw_data_items:
        filtered_data_item = {}
        #Iterate over every key of interest"
        for item_key_of_interest in item_keys_of_interest:
            try:
                filtered_data_item[item_key_of_interest] = raw_data_item[item_key_of_interest]
            except KeyError:
                filtered_data_item[item_key_of_interest] = "NULL"

        filtered_data_items.append(filtered_data_item)

    return filtered_data_items 

def translate_bpfs_to_status(engagement_id_list):
    max_items_in_filter = int(helper_config.get_config_item("API", "MAX_NUM_ITEMS_IN_FILTER"))
    bpf_collection_api_url  = helper_config.get_config_item("API",  "URL_GET_BPFs")

    if len(engagement_id_list) <= max_items_in_filter:
        query_filters = [_create_bpf_query_filter(engagement_id_list)]
    else:
        engagement_sublists = [engagement_id_list[x:x+max_items_in_filter] for x in range(0, len(engagement_id_list), max_items_in_filter)]
        query_filters = [_create_bpf_query_filter(engagement_id_list) for engagement_id_list in engagement_sublists ]

    bpf_mapped_results = []

    for query_filter in query_filters:
        bpf_api_response_for_filter      = map_filter_query_in_api(query_filter, bpf_collection_api_url )
        bpf_filtered_responses_for_query_filter = filter_data_items(bpf_api_response_for_filter, bpf_keys_of_interest)
        
        for bpf_filtered_response_for_query_filter in bpf_filtered_responses_for_query_filter:
            bpf_status_id  = bpf_filtered_response_for_query_filter[bpf_status_field]
            engagement_status = engagement_bpf_status_id_to_number[bpf_status_id]
            bpf_filtered_response_for_query_filter[engagement_status_field] = engagement_status
            del bpf_filtered_response_for_query_filter[bpf_status_field]

        bpf_mapped_results += bpf_filtered_responses_for_query_filter
    

    return bpf_mapped_results

def _create_bpf_query_filter(engagement_id_sublist):
    bpf_filter_template = "_bpf_msp_engagementid_value eq '{}'"
    join_string = " or "

    filter_list = [ bpf_filter_template.format(engagement_id) for engagement_id in engagement_id_sublist ]
    filter = join_string.join(filter_list)

    return filter


