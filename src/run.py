import os
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, "static/examples/example1/", "universe.db")

# TODO: Read millenium facon's JSON file to retrieve routes_db


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/routes")
def routes():
    conn = get_db_connection()
    routes = conn.execute("SELECT * FROM routes").fetchall()
    conn.close()
    return render_template("routes.html", routes=routes)


app.run(debug=True)
