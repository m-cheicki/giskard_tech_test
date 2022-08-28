import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, json, request


app = Flask(__name__)
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
RELATIVE_PATH = "static/examples/example1/"
MILLENIUM = json.load(
    open(os.path.join(PROJECT_ROOT, RELATIVE_PATH, "millennium-falcon.json"))
)
DATABASE = os.path.join(PROJECT_ROOT, RELATIVE_PATH, MILLENIUM["routes_db"])


def get_db_connection(filename):
    conn = sqlite3.connect(filename)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_routes():
    conn = get_db_connection(DATABASE)
    routes = conn.execute("SELECT * FROM routes").fetchall()
    conn.close()
    return routes


def get_routes_from_origin(origin):
    conn = get_db_connection(DATABASE)
    routes = conn.execute(f"SELECT * FROM routes WHERE origin = '{origin}'").fetchall()
    conn.close()
    return routes


def get_travel_time_from_origin_to_destination(origin, destination):
    conn = get_db_connection(DATABASE)
    travel_time = conn.execute(
        f"SELECT travel_time FROM routes WHERE origin = '{origin}' AND destination = '{destination}'"
    ).fetchall()
    conn.close()
    return travel_time


def get_all_origin():
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


def format_bounty_hunters(empire):
    graph = {}
    for _ in empire["bounty_hunters"]:
        if _["planet"] in graph:
            days = graph[_["planet"]]
        else:
            days = []
        days.append(_["day"])
        graph[_["planet"]] = days
    return graph


def has_seen_bounty_hunters(empire, path, days):
    possible_capture = []
    bounty_hunters = format_bounty_hunters(empire)
    if list(bounty_hunters.keys()) in path:
        for key, value in bounty_hunters.items():
            possible_capture.append(days in value)
    return sum(possible_capture)


def get_days_of_travel_from_path(path):
    days = 0
    for i in range(len(path) - 1):
        traveling_times = get_travel_time_from_origin_to_destination(
            path[i], path[i + 1]
        )
        days += traveling_times[0]["travel_time"]
    return days


def get_all_days_of_travel(paths, empire):
    travels = []
    counts = []
    for _ in range(len(paths)):
        days = get_days_of_travel_from_path(paths[_])
        count = has_seen_bounty_hunters(empire, paths[_], days)
        days += days // MILLENIUM["autonomy"]
        travels.append(days)
        counts.append(count)
    return travels, counts


def compute_probability(x):
    if x == 1:
        p = 1 / 10
    elif x > 1:
        p = 1 / 10
        for i in range(x):
            p += (9**i) / (10 ** (i + 1))
    else:
        p = 0
    return 1 - p


def get_probability(countdown, df):
    probabilities = []
    for i in df.index:
        if countdown < df["total_travel_time"][i]:
            probabilities.append(0)
        else:
            probabilities.append(df["probability"][i] * 100)
    return probabilities


# ROUTES
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        empire = json.load(request.files["file"])
        travels, counts = get_all_days_of_travel(paths, empire)
        df = pd.DataFrame(
            zip(paths, travels, counts),
            columns=["path", "total_travel_time", "nb_bounty_hunters"],
        )
        df["probability"] = df["nb_bounty_hunters"].apply(compute_probability)
        probabilities = get_probability(empire["countdown"], df)
        return render_template(
            "empire.html",
            empire=empire,
            probabilities=probabilities,
        )


@app.route("/routes")
def routes():
    routes = get_all_routes()
    return render_template("routes.html", routes=routes)


if __name__ == "__main__":
    graph = create_graph()
    paths = find_all_paths(graph, "Tatooine", "Endor")
    app.run(debug=True)
