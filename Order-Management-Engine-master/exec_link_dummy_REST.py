import flask
from flask_pymongo import PyMongo

import time
import datetime

import requests
import json

app = flask.Flask(__name__)


@app.route("/execution_REST_API_dummy", methods=["POST"])  ##dummy REST API
def execution_links_accept():
    # initialize the ack dictionary that will be returned from the view
    ack = {"success": False}

    if flask.request.method == "POST":
        # print request.data
        if flask.request.is_json:
            content = flask.request.get_json()
            print("execution_REST_API_dummy")
            print(content)

            ack["success"] = True

    return flask.jsonify(ack)


if __name__ == "__main__":
    print(("* Flask starting server..."
           "Please wait until server has fully started"))
    app.run(port=5001, debug=True)
