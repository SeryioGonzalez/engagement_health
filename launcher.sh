#!/bin/bash

installation_dir="/home/sergio/python/crm-engagement-checker/"

function read_config {
    category=$1
    item=$2
    
    crudini --get $installation_dir"config.ini" $category $item | sed "s/'//g"
}

echo "DELETING TEMP DATA"
temp_file_folder=$installation_dir$(read_config FILES TEMP_FOLDER)
find $temp_file_folder -type f -name "*json" -exec rm {} \;

echo "FLUSHING MILESTONES AND ENGAGEMENTS"
cd $installation_dir && python3 0_crm_engagement_flush_milestones_and_engagements.py

echo "COLLECT DATA"
cd $installation_dir && python3 1_crm_engagement_data_collector.py

echo "CHECK_RESULTS"
engagement_check_results_folder=$(read_config "FILES" "CHECK_RESULT_FOLDER")
engagement_check_results_filename_template=$(read_config "FILES" "CHECK_RESULT_FILENAME_TEMPLATE")
now_string=$( date +%Y%m%d_%H%M%S)
engagement_check_results_file=$engagement_check_results_folder$(echo $engagement_check_results_filename_template | sed "s/{}/$now_string/")
echo "RESULTS WILL GO IN $engagement_check_results_file"
cd $installation_dir && python3 2_crm_engagement_checker.py $engagement_check_results_file

echo "SENDING NOTIFICATIONS FROM $engagement_check_results_file"
cd $installation_dir && python3 3_crm_engagement_notifications.py $engagement_check_results_file