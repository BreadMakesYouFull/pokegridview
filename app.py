from flask import Flask, render_template, send_from_directory
from pathlib import Path

app = Flask(__name__)

GALLERY_DIR = Path("static/gallery")

@app.route("/")
def index():
    # List all images
    images = sorted(
        f.name for f in GALLERY_DIR.glob("*")
    )
    return render_template("index.html", images=images)

@app.route("/images/<filename>")
def serve_image(filename):
    return send_from_directory(GALLERY_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
