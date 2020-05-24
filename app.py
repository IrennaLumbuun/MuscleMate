from detector import *
from flask import Flask, flash, request, redirect, url_for
#import threading
from werkzeug.utils import secure_filename
import io
#lock = threading.Lock()

app = Flask(__name__)

@app.route("/")
def run_main():
    return "great job!"

@app.route("/detector", methods =["POST"])
def detect_motion():
    data = request.data
    encoded_data = data.split(',')[1]
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow(img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(debug=True)