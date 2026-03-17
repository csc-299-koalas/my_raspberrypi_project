from gpiozero import MotionSensor
from picamera2 import Picamera2
import requests
import time

pir = MotionSensor(18)
cam = Picamera2()
cam.start()

last = 0

while True:
    pir.wait_for_motion()

	# 5 seconds between requests to reduce spam
    if time.time() - last > 5:
        cam.capture_file("pic.jpg")

        f = open("pic.jpg", "rb")
        requests.post("http://172.20.10.9:8080/upload", files={"file": f})
        f.close()

        last = time.time()