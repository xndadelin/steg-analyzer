import os
import subprocess
import magic
from flask import Flask, render_template, request, send_file, jsonify

from werkzeug.utils import secure_filename
import uuid
from PIL import Image, ImageEnhance, ImageFilter
import io

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    'png',
    'jpg',
    'jpeg',
    'bmp',
    'gif',
    'tiff'
}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return """
    <h1>hello, steg-analyzer!</h1>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)