from detector import *
from flask import Flask, flash, request, redirect, url_for
import threading
from werkzeug.utils import secure_filename

lock = threading.Lock()

app = Flask(__name__)
@app.route("/")
def run_main():
    return "great job!"

if __name__ == '__main__':
    app.run(debug=True)