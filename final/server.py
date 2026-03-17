from bottle import Bottle, request, run, template, response
import os
import time
import threading
from gpiozero import Buzzer
import smtplib

app = Bottle()

PIN = "0000"
LAST_IMAGE = "latest.jpg"
LAST_TIME = None

GMAIL_USER = 'koalascsc299@gmail.com'
GMAIL_PASS = 'your password'
SMTP_SERVER = 'smtp.gmail.com' # or other SMTP server
SMTP_PORT = 587

ENTRY_DELAY = 60

# alarm state
disarmed = True
entry_deadline = None
alarm_triggered = False

# buzzer
buzzer = Buzzer(18)


def buzzer_loop():
    global alarm_triggered

    while alarm_triggered:
        buzzer.on()
        time.sleep(0.4)
        buzzer.off()
        time.sleep(0.4)

def send_email(recipient, subject, text):
    smtpserver = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(GMAIL_USER, GMAIL_PASS)
    header = 'To:' + recipient + '\n' + 'From: ' + GMAIL_USER
    header = header + '\n' + 'Subject:' + subject + '\n'
    msg = header + '\n' + text + ' \n\n'
    smtpserver.sendmail(GMAIL_USER, recipient, msg)
    smtpserver.close()

def trigger_alarm():
    global alarm_triggered

    if not alarm_triggered:
        alarm_triggered = True
        send_email('mmrocze1@depaul.edu', 'Alarm Triggered', 'The alarm has been triggered at ' + time.strftime("%Y-%m-%d %H:%M:%S"))
        threading.Thread(target=buzzer_loop, daemon=True).start()


def stop_alarm():
    global alarm_triggered
    alarm_triggered = False
    buzzer.off()


def entry_timer():
    global entry_deadline

    while entry_deadline and time.time() < entry_deadline and not disarmed:
        time.sleep(1)

    if not disarmed and entry_deadline:
        trigger_alarm()


@app.post("/upload")
def upload():
    global LAST_TIME, entry_deadline

    file = request.files.get("file")

    if file:
        file.save(LAST_IMAGE, overwrite=True)
        LAST_TIME = time.strftime("%Y-%m-%d %H:%M:%S")

        # start entry delay if armed
        if not disarmed and entry_deadline is None:
            entry_deadline = time.time() + ENTRY_DELAY
            threading.Thread(target=entry_timer, daemon=True).start()

    return "ok"


@app.get("/")
def panel():
    return template("alarm")


@app.get("/image")
def image():
    if os.path.exists(LAST_IMAGE):
        response.content_type = "image/jpeg"
        return open(LAST_IMAGE, "rb").read()
    return ""


@app.get("/status")
def status():

    remaining = None
    if entry_deadline:
        remaining = max(0, int(entry_deadline - time.time()))

    return {
        "armed": not disarmed,
        "last_time": LAST_TIME,
        "has_image": os.path.exists(LAST_IMAGE),
        "entry_delay": remaining,
        "alarm": alarm_triggered
    }


@app.post("/arm")
def arm():
    global disarmed, entry_deadline

    disarmed = False
    entry_deadline = None
    stop_alarm()

    return {"ok": True}


@app.post("/disarm")
def disarm():
    global disarmed, entry_deadline

    data = request.json

    if data and data.get("pin") == PIN:
        disarmed = True
        entry_deadline = None
        stop_alarm()
        return {"ok": True}

    response.status = 403
    return {"error": "invalid pin"}


run(app, host="0.0.0.0", port=8080)