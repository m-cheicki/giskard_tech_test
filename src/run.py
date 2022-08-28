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


def get_travel_time_from_origin_to_destination(origin, destination):
    config = get_config()
    DATABASE = os.path.join(PROJECT_ROOT, RELATIVE_PATH, config["routes_db"])
    conn = get_db_connection(DATABASE)
    travel_time = conn.execute(
        f"SELECT travel_time FROM routes WHERE origin = '{origin}' AND destination = '{destination}'"
    ).fetchall()
    conn.close()
    return travel_time


def get_all_origin():
    config = get_config()
    DATABASE = os.path.join(PROJECT_ROOT, RELATIVE_PATH, config["routes_db"])
    conn = get_db_connection(DATABASE)
    routes = conn.execute(f"SELECT DISTINCT origin FROM routes").fetchall()
    conn.close()
    return routes


def create_graph():
    origins = get_all_origin()
    graph = {}
    for i in range(len(origins)):
        destinations = get_routes_from_origin(origins[i]["origin"])
        graph[origins[i]["origin"]] = [
            destinations[_]["destination"] for _ in range(len(destinations))
        ]
    return graph


def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths


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
    graph = create_graph()
    paths = find_all_paths(graph, "Tatooine", "Endor")
    travels = []
    for i in range(len(paths)):
        path = paths[i]
        total_travel_time = []
        time = 0
        for j in range(len(path) - 1):
            traveling_times = get_travel_time_from_origin_to_destination(
                path[j], path[j + 1]
            )
            time += traveling_times[0]["travel_time"]
        total_travel_time.append(time)
        print(total_travel_time)
    routes = get_all_routes()
    return render_template("routes.html", routes=routes)


if __name__ == "__main__":
    app.run(debug=True)
