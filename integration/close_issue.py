#!/usr/bin/env python3

import requests
import sqlite3
import sys
import logging
import re

# Configuration for Redmine API
REDMINE_URL = 'your_redmine_url/issues'
REDMINE_API_KEY = 'redmine_api_key'
REDMINE_STATUS_ID_CLOSED = 2  # Replace with the your closed status ID

# Setup logging
logging.basicConfig(filename='/var/log/zabbix/close_issue.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# SQLite database connection
db_file = '/home/ubuntu/redmine_database.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def close_redmine_issue(issue_id):
    url = f'{REDMINE_URL}/{issue_id}.json'
    headers = {
        'Content-Type': 'application/json',
        'X-Redmine-API-Key': REDMINE_API_KEY
    }

    payload = {
        'issue': {
            'status_id': REDMINE_STATUS_ID_CLOSED
        }
    }

    logging.info(f"Closing issue {issue_id} with payload: {payload}")

    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()

        if response.status_code in [200, 204]:
            logging.info(f'Issue {issue_id} closed successfully in Redmine.')
            return True
        else:
            logging.error(f'Failed to close issue in Redmine. Status code: {response.status_code}, Error: {response.text}')
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f'Error closing issue: {e}')
        return False

def get_issue_by_alert_id(alert_id):
    try:
        cursor.execute('SELECT issue_id FROM issue_tracking WHERE alert_id = ? AND status = "open"', (alert_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f'Error retrieving issue for alert ID {alert_id} from database: {e}')
        return []

def mark_issue_closed(alert_id):
    try:
        cursor.execute('UPDATE issue_tracking SET status = "closed" WHERE alert_id = ?', (alert_id,))
        conn.commit()
        logging.info(f'Marked issue for alert ID {alert_id} as closed in the database.')
    except sqlite3.Error as e:
        logging.error(f'Error updating issue status in database: {e}')

def extract_event_id_from_description(description):
    match = re.search(r'Original problem ID: (\d+)', description)
    if match:
        return match.group(1)
    else:
        logging.error("Failed to extract Event ID from description")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: close_issue.py <description>")
        sys.exit(1)

    description = sys.argv[1]

    logging.info(f"Received description: {description}")

    alert_id = extract_event_id_from_description(description)

    if alert_id:
        logging.info(f"Extracted alert_id: {alert_id}")
        issues_to_close = get_issue_by_alert_id(alert_id)

        if issues_to_close:
            for issue_id, in issues_to_close:
                if close_redmine_issue(issue_id):
                    mark_issue_closed(alert_id)
        else:
            logging.info(f"No open issues found for alert ID {alert_id}")
    else:
        logging.error("No valid alert ID found in description")

    cursor.close()
    conn.close()
    logging.info("Finished processing")
