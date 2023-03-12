import requests
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import requests

# Replace the URL, username, and password with your Jira API endpoint and credentials
JIRA_URL = 'https://your-jira-url.com/rest/api/2/search'
JIRA_USERNAME = 'your-jira-username'
JIRA_PASSWORD = 'your-jira-password'

# Connect to the database
engine = create_engine('postgresql://user:password@localhost/database_name')
Session = sessionmaker(bind=engine)
Base = declarative_base()

# Define the Ticket class
class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    number = Column(String)
    name = Column(String)
    description = Column(String)
    reporter = Column(String)
    status = Column(String)
    due_date = Column(DateTime)

# Authenticate with the Jira API
auth = (JIRA_USERNAME, JIRA_PASSWORD)

# Fetch tickets using pagination
start_at = 0
max_results = 50
tickets = []

while True:
    params = {'jql': 'project = YOUR_PROJECT', 'startAt': start_at, 'maxResults': max_results}
    response = requests.get(JIRA_URL, auth=auth, params=params)
    data = response.json()

    if not data['issues']:
        break

    tickets += data['issues']
    start_at += max_results

# Save tickets in the database
session = Session()

for ticket in tickets:
    t = Ticket(
        number=ticket['key'],
        name=ticket['fields']['summary'],
        description=ticket['fields']['description'],
        reporter=ticket['fields']['reporter']['displayName'],
        status=ticket['fields']['status']['name'],
        due_date=ticket['fields']['dueDate']
    )
    session.add(t)

session.commit()
session.close()



# Replace the URL, username, and password with your Jira API endpoint and credentials
JIRA_URL = 'https://your-jira-url.com/rest/api/2/issue/YOUR_TICKET_KEY_OR_ID/transitions'
JIRA_USERNAME = 'your-jira-username'
JIRA_PASSWORD = 'your-jira-password'

# Authenticate with the Jira API
auth = (JIRA_USERNAME, JIRA_PASSWORD)

# Define the payload to update the ticket status and add a comment
payload = {
    'transition': {
        'id': 'YOUR_TRANSITION_ID_FOR_CLOSED_STATUS'
    },
    'update': {
        'comment': [
            {
                'add': {
                    'body': 'YOUR_COMMENT_BODY'
                }
            }
        ]
    }
}

# Send the PUT request to update the ticket status and add a comment
response = requests.put(JIRA_URL, auth=auth, json=payload)

# Check the response status code to ensure that the ticket was updated successfully
if response.status_code == 204:
    print('Ticket status updated and comment added successfully!')
else:
    print('Failed to update ticket status and comment.')
