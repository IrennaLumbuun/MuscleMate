from BackEnd.detector import *
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import time
import cv2

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("./firstpage.html")

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)