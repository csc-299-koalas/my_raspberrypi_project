from gpiozero import MotionSensor
from picamera2 import Picamera2
import requests
import time

pir = MotionSensor(4)
cam = Picamera2()
cam.start()

last = 0

while True:
    pir.wait_for_motion()

	# 10 seconds between requests to reduce spam
    if time.time() - last > 10:
        cam.capture_file("pic.jpg")

        f = open("pic.jpg", "rb")
        requests.post("http://ip:8080/upload", files={"file": f})
        f.close()

        last = time.time()