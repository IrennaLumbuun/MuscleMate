from detector import *
from flask import Flask, flash, request, redirect, url_for, Response
from pprint import pprint
import threading
from werkzeug.utils import secure_filename
import io
from flask_cors import CORS
import cv2
import time

lock = threading.Lock()

app = Flask(__name__)
CORS(app)


@app.route("/detector", methods =["POST"])
def POST():
    data = request.data.decode('UTF-8')
    '''
    encoded_data = data.split(',')[1]
    nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imshow(img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    print(request.headers)
    print(request.__dict__)
    return "200"

def run_detector():
    vs = cv2.VideoCapture(0)
    time.sleep(0.5) # give some time to warm up

    cv2.namedWindow('Tracking')
    vs.set(3, 600)
    vs.set(4, 450)

    cv2.createTrackbar("minArea", "Tracking", 5000, 20000, nothing)

    cv2.createTrackbar('LH', 'Tracking', 75, 255, nothing)
    cv2.createTrackbar('LS', 'Tracking', 43, 255, nothing)
    cv2.createTrackbar('LV', 'Tracking', 0, 255, nothing)

    cv2.createTrackbar('UH', 'Tracking', 129, 255, nothing)
    cv2.createTrackbar('US', 'Tracking', 101, 255, nothing)
    cv2.createTrackbar('UV', 'Tracking', 208, 255, nothing)
    
    hand1_loc = deque(maxlen= 50)
    hand2_loc = deque(maxlen= 50)

    reach_target = 0

    outputFrame = None

    while True:
        print("runnign detector....")
        ret, frame = vs.read()
        if not ret:
            print("no frame to read")
            break

        with lock:
            if outputFrame is None:
                continue
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag: 
                continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')
    
        minArea = cv2.getTrackbarPos('minArea', 'Tracking')

        mask = maskImage(frame)
        contour = getContour(mask)
        #cv2.imshow('Tracking', mask)

        populateDeque(frame, contour, minArea, hand1_loc, hand2_loc)
        draw_movement(frame, hand1_loc, hand2_loc)

        #draw target
        frame = cv2.rectangle(frame, (0, 0), (650, 70), (255, 0, 0), -1)
        frame = cv2.putText(frame, "Target", (275, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)
        frame = cv2.circle(frame, (40, 33), 30, (255, 255, 255), -1)
        frame = cv2.putText(frame, str(reach_target), (30, 37), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 3)

        if(len(hand1_loc) > 1):
            last_posY = hand1_loc[len(hand1_loc) - 1][1]
            last_posX = hand1_loc[len(hand1_loc) - 1][0]

            print(last_posX, last_posY)
            #user has hit target
            if hand1_loc[len(hand1_loc) - 1][1] <= 70 and hand1_loc[len(hand1_loc) - 1][1] > hand1_loc[len(hand1_loc) - 2][1]:
                reach_target += 1

        with lock: 
            outputFrame = frame.copy()

        #cv2.imshow('Contour', frame)

        #key = cv2.waitKey(1) & 0xFF
        #if key == 'q' or key == 27:
        #    break
    print("running")
    vs.release()
    cv2.destroyAllWindows()

@app.route("/launch", methods =["POST"])
def launch():
    data = request.form['click']
    if data == "clicked":
        print("run detector")
        run_detector()

    return "200"

@app.route("/run_vid")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    app.run(debug=True)