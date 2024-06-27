 cat create_issue.py
#!/usr/bin/env python3

import requests
import sqlite3
import sys
import logging
import re

# Configuration for Redmine API
REDMINE_URL = 'your_remine_url/issues.json'
REDMINE_API_KEY = 'RedmineAPIKEY'
REDMINE_PROJECT_ID = 3 #Project ID
REDMINE_TRACKER_ID = 1 #Tracker ID
REDMINE_STATUS_ID_OPEN = 1 #Issue status ID
REDMINE_PRIORITY_ID = 2 

# SQLite database connection
conn = sqlite3.connect('/home/ubuntu/redmine_database.db')
cursor = conn.cursor()

# Setup logging
logging.basicConfig(filename='/var/log/zabbix/create_issue.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def create_redmine_issue(subject, description):
    headers = {
        'Content-Type': 'application/json',
        'X-Redmine-API-Key': REDMINE_API_KEY
    }

    payload = {
        'issue': {
            'project_id': REDMINE_PROJECT_ID,
            'tracker_id': REDMINE_TRACKER_ID,
            'status_id': REDMINE_STATUS_ID_OPEN,
            'subject': subject,
            'description': description,
            'priority_id': REDMINE_PRIORITY_ID
        }
    }

    try:
        response = requests.post(REDMINE_URL, headers=headers, json=payload)
        response.raise_for_status()

        if response.status_code == 201:
            issue_id = response.json()['issue']['id']
            logging.info(f'Issue created successfully in Redmine. Issue ID: {issue_id}')
            return issue_id
        else:
            logging.error(f'Failed to create issue in Redmine. Status code: {response.status_code}, Error: {response.text}')
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f'Error creating issue: {e}')
        return None

def store_issue_id(alert_id, issue_id):
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO issue_tracking (alert_id, issue_id, status)
            VALUES (?, ?, 'open')
        ''', (alert_id, issue_id))
        conn.commit()
        logging.info(f'Stored issue ID {issue_id} for alert ID {alert_id} in database.')
    except sqlite3.Error as e:
        logging.error(f'Error storing issue ID in database: {e}')

def extract_event_id(description):
    match = re.search(r'Original problem ID:\s*(\d+)', description)
    if match:
        return match.group(1)
    else:
        logging.error('Failed to extract event ID from description')
        return None

if __name__ == "__main__":
    logging.info(f"Received arguments: {sys.argv}")

    if len(sys.argv) < 4:
        print("Usage: create_issue.py <alert_id> <subject> <description>")
        sys.exit(1)

    alert_id = sys.argv[1]
    subject = sys.argv[2]
    description = sys.argv[3]

    logging.info(f"Received alert_id: {alert_id}, subject: {subject}, description: {description}")

    # Extract event ID from description
    event_id = extract_event_id(description)
    if event_id:
        logging.info(f"Extracted event_id: {event_id}")
    else:
        logging.error("Failed to extract event ID from description")
        sys.exit(1)

    issue_id = create_redmine_issue(subject, description)
    if issue_id:
        store_issue_id(event_id, issue_id)

    cursor.close()
    conn.close()
