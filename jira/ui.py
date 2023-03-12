from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

# Replace the connection details with your own database connection details
conn = psycopg2.connect(database="your-database-name", user="your-database-user", password="your-database-password", host="your-database-host", port="your-database-port")

@app.route("/")
def index():
    cur = conn.cursor()
    cur.execute("SELECT number, name, description, reporter, status, due_date FROM tickets")
    tickets = cur.fetchall()
    cur.close()
    return render_template("tickets.html", tickets=tickets)

if __name__ == "__main__":
    app.run()
