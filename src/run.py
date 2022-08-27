import os
import sqlite3
from flask import Flask, render_template, json, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = "static/examples/example1/"
EMPIRE_PATH = "static/empire/"


def get_config():
    CONFIG_FILE = os.path.join(PROJECT_ROOT, RELATIVE_PATH, "millennium-falcon.json")
    return json.load(open(CONFIG_FILE))


def get_db_connection(filename):
    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_routes():
    config = get_config()
    DATABASE = os.path.join(PROJECT_ROOT, RELATIVE_PATH, config["routes_db"])
    conn = get_db_connection(DATABASE)
    routes = conn.execute("SELECT * FROM routes").fetchall()
    conn.close()
    return routes


def get_routes_from_origin(origin):
    config = get_config()
    DATABASE = os.path.join(PROJECT_ROOT, RELATIVE_PATH, config["routes_db"])
    conn = get_db_connection(DATABASE)
    routes = conn.execute(f"SELECT * FROM routes WHERE origin = '{origin}'").fetchall()
    conn.close()
    return routes


def get_route_from_origin(origin):
    total_day = 0
    while origin != "Endor":
        routes = get_routes_from_origin(origin)
        for i in range(len(routes)):
            origin = routes[i]["destination"]
            total_day = total_day + int(routes[i]["travel_time"])
    print(total_day)


# ROUTES
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        empire = request.files["file"]
        empire = json.load(empire)
        return render_template("empire.html", empire=empire, probability=0)


@app.route("/routes")
def routes():
    routes = get_all_routes()
    get_route_from_origin("Tatooine")
    return render_template("routes.html", routes=routes)


if __name__ == "__main__":
    app.run(debug=True)
