from flask import Flask, render_template, request, flash
import requests
import psycopg2

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Replace the connection details with your own database connection details
conn = psycopg2.connect(database="your-database-name", user="your-database-user", password="your-database-password", host="your-database-host", port="your-database-port")

# Replace the URL, username, and password with your Jira API endpoint and credentials
JIRA_URL = 'https://your-jira-url.com/rest/api/2/search'
JIRA_USERNAME = 'your-jira-username'
JIRA_PASSWORD = 'your-jira-password'

@app.route("/")
def index():
    cur = conn.cursor()
    cur.execute("SELECT number, name, description, reporter, status, due_date FROM tickets")
    tickets = cur.fetchall()
    cur.close()
    return render_template("tickets.html", tickets=tickets)

@app.route("/fetch-tickets", methods=["POST"])
def fetch_tickets():
    cur = conn.cursor()
    cur.execute("SELECT number FROM tickets")
    existing_tickets = set([row[0] for row in cur.fetchall()])
    cur.close()

    auth = (JIRA_USERNAME, JIRA_PASSWORD)
    payload = {
        'jql': 'YOUR_JIRA_QUERY',
        'maxResults': 100
    }

    response = requests.get(JIRA_URL, auth=auth, params=payload)

    if response.status_code == 200:
        new_tickets = []
        for ticket in response.json()['issues']:
            if ticket['key'] not in existing_tickets:
                number = ticket['key']
                name = ticket['fields']['summary']
                description = ticket['fields']['description']
                reporter = ticket['fields']['reporter']['displayName']
                status = ticket['fields']['status']['name']
                due_date = ticket['fields'].get('duedate', None)
                new_tickets.append((number, name, description, reporter, status, due_date))

        cur = conn.cursor()
        cur.executemany("INSERT INTO tickets (number, name, description, reporter, status, due_date) VALUES (%s, %s, %s, %s, %s, %s)", new_tickets)
        conn.commit()
        cur.close()

        flash(f"{len(new_tickets)} new tickets fetched and inserted into the database!")
    else:
        flash("Failed to fetch new tickets from Jira.")

    return render_template("tickets.html")

if __name__ == "__main__":
    app.run()
