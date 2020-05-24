from BackEnd.detector import *
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import datetime
import imutils
import time
import cv2

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("./firstpage.html")
