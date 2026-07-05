from flask import Flask, render_template, redirect
import hashlib
import os
import json

app = Flask(__name__)

MONITOR_FOLDER = "monitored_files"
BASELINE_FILE = "baseline.json"


def calculate_hash(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:

        while chunk := f.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_baseline():

    baseline = {}

    for filename in os.listdir(MONITOR_FOLDER):

        path = os.path.join(
            MONITOR_FOLDER,
            filename
        )

        if os.path.isfile(path):

            baseline[filename] = calculate_hash(
                path
            )

    with open(BASELINE_FILE, "w") as file:

        json.dump(
            baseline,
            file,
            indent=4
        )


def scan_changes():

    with open(BASELINE_FILE, "r") as file:

        baseline = json.load(file)

    current = {}

    modified = []
    added = []
    deleted = []

    for filename in os.listdir(MONITOR_FOLDER):

        path = os.path.join(
            MONITOR_FOLDER,
            filename
        )

        if os.path.isfile(path):

            current[filename] = calculate_hash(
                path
            )

    for file, hash_value in current.items():

        if file not in baseline:

            added.append(file)

        elif baseline[file] != hash_value:

            modified.append(file)

    for file in baseline:

        if file not in current:

            deleted.append(file)

    return {
        "modified": modified,
        "added": added,
        "deleted": deleted
    }


@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/baseline")
def baseline():

    create_baseline()

    return redirect("/scan")


@app.route("/scan")
def scan():

    results = scan_changes()

    return render_template(
        "index.html",
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)