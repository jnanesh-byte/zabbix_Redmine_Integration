Zabbix-Redmine Integration
This project provides an integration between Zabbix 6 and Redmine for automated issue management. It includes scripts to create and close Redmine issues based on Zabbix alert triggers.

Prerequisites
Zabbix 6
Redmine
Python 3
SQLite3

Setup
1. Configure Redmine
Ensure that you have Redmine set up and accessible. You will need an API key for authentication.

2. Configure Zabbix
In Zabbix, configure media types and actions to execute the scripts when alerts are triggered.

3. create_issue.py
This script creates a new issue in Redmine when an alert is triggered in Zabbix.

4. close_issue.py
This script closes the issue in Redmine when the alert is resolved in Zabbix.

6. Configure Zabbix Media Types and Actions

Media Types
Go to Administration > Media types.
Create a new media type with the following details:
Name: Redmine Integration
Type: Script
Script name: create_issue.py
Script parameters:
{EVENT.ID}
{TRIGGER.NAME}
{ALERT.MESSAGE}

Actions
Go to Configuration > Actions.
Create a new action with the following details:
Name: Create Redmine Issue
Condition: As per your requirements.
Operations: Add a new operation to use the Redmine Integration media type.


Conclusion
With these steps, you will have a functional integration between Zabbix and Redmine that automates the creation and closure of issues based on alert triggers. This setup improves efficiency and ensures that all alerts are properly tracked and managed in Redmine.


