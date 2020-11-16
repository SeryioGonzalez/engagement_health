#!/bin/bash

installation_dir="/home/sergio/python/crm-engagement-checker/"
set -e

send_report=$1

function read_config {
    category=$1
    item=$2
    
    crudini --get $installation_dir"config.ini" $category $item | sed "s/'//g"
}


echo "MANAGING FIREWALL RULES"
resource_group_name=$(read_config "AZURE" "RESOURCE_GROUP")
subscription=$(read_config "AZURE" "SUBSCRIPTION")
database_server_name=$(read_config "SQL" "DATABASE_SERVER")

az account set --subscription $subscription

echo "DELETE OLD RULE"
existing_rule_name=$(az mysql server firewall-rule list --resource-group $resource_group_name --server-name $database_server_name  --query "[?contains(name,'ClientIPAddress_')].name" -o tsv)
if [ "fff$existing_rule_name" != "fff" ]
then
    az mysql server firewall-rule delete --name $existing_rule_name --resource-group $resource_group_name --server-name $database_server_name --yes
fi

echo "CREATE FIREWALL RULE"
my_public_ip=$(dig +short myip.opendns.com @resolver1.opendns.com)
az mysql server firewall-rule create --name "ClientIPAddress_"$(date +%Y%m%d) --resource-group $resource_group_name --server-name $database_server_name --start-ip-address $my_public_ip --end-ip-address $my_public_ip > /dev/null

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

if [ "fff$send_report" != "fff" ]
then
    echo "SENDING NOTIFICATIONS FROM $engagement_check_results_file"
    cd $installation_dir && python3 3_crm_engagement_notifications.py $engagement_check_results_file
else 
    echo "CHECKING FOR SERGIO NOTIFICATIONS"
    jq -r ".[].affected_items[].engagement_owner" $engagement_check_results_file | grep -i sergio

    if [ $? -eq 0 ]
    then
        echo "SENDING EMAIL"
        cd $installation_dir && python3 4_send_email_self.py $engagement_check_results_file
    fi

fi

