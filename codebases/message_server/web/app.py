
import os
import psycopg
from flask import Flask, request, redirect, url_for, render_template
from markupsafe import escape

    # The app can run in two 'modes' — production mode, or development mode.
    # This is determined by the `APP_ENV` environment variable.

def get_database_url():
    if os.environ.get("APP_ENV") == "PRODUCTION":
        password = os.environ.get("POSTGRES_PASSWORD")
        hostname = os.environ.get("POSTGRES_HOSTNAME")
        return f"postgres://postgres:{password}@{hostname}:5432/postgres"
    else:
        # This URL is for our local database. You may need to edit it.
        return "postgres://localhost:5432/postgres"

def setup_database(url):
    # We connect using the URL
    connection = psycopg.connect(url)
    # Get a 'cursor' object that we can use to run SQL
    cursor = connection.cursor()
    # Execute some SQL to create the table
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (message TEXT);")
    # And commit the changes to ensure that they 'stick' in the database.
    connection.commit()

# We run the two functions above
POSTGRES_URL = get_database_url()
setup_database(POSTGRES_URL)

app = Flask(__name__)

@app.route("/")
def get_messages():
    connection = psycopg.connect(POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages;")
    messages = cursor.fetchall()
    return render_template('messages.html', messages=messages)


    # Format the results and add a form too
    # return format_messages(rows) + generate_form()



# These two methods generate HTML lists and forms

# def format_messages(messages):
#     output = "<ul>"
#     for message in messages:
#         # We escape the message to avoid the user sending us HTML and tricking
#         # us into rendering it.
#         escaped_message = escape(message[0])
#         output += f"<li>{escaped_message}</li>"
#     output += "</ul>"
#     return output

# def generate_form():
#     return """
#     <form action="/" method="POST">
#         <input type="text" name="message">
#         <input type="submit" value="Send">
#     </form>
#     """

# This method receives the POST request from the form above
@app.route("/", methods=["POST"])
def post_message():
    # We extract the message from the request
    message = request.form["message"]

    # Insert a new message record into the database
    connection = psycopg.connect(POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO messages (message) VALUES (%s);", (message,))
    connection.commit()

    # And redirect to the main page
    return redirect(url_for("get_messages"))

if __name__ == '__main__':
    # We run the server differently depending on the environment.
    # In production we don't want the fancy error messages, so no `debug=True`
    if os.environ.get("APP_ENV") == "PRODUCTION":
        app.run(port=5000, host='0.0.0.0')
    else:
        app.run(debug=True, port=5000, host='0.0.0.0')
