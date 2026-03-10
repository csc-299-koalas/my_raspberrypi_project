from bottle import Bottle, request, run
import os
import time

app = Bottle()

LAST_IMAGE = "latest.jpg"
LAST_TIME = None


@app.post("/upload")
def upload():
    global LAST_TIME

    file = request.files.get("file")

    if file:
        file.save(LAST_IMAGE, overwrite=True)
        LAST_TIME = time.strftime("%Y-%m-%d %H:%M:%S")

    return "ok"


@app.get("/")
def home():
    if os.path.exists(LAST_IMAGE):
        return f"""
        <h1>Latest Motion</h1>
        <p>Time: {LAST_TIME}</p>
        <img src="/image" width="500">
        """
    else:
        return "<h1>No images yet</h1>"


@app.get("/image")
def image():
    return open(LAST_IMAGE, "rb").read()

run(app, host="0.0.0.0", port=8080)