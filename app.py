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

def get_file_type(filepath):
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(filepath)
        return file_type
    except:
        return "unknown" 
    
def run_command(command, timeout=500):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timed out. Please try again or contact support if the issue persists.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    
def analyze_with_binwalk(filepath, output_dir):
    command = f"binwalk -dd='*' -e {filepath} -C {output_dir}"
    result = run_command(command)

    extracted_files = []
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                extracted_files.append(os.path.join(root, file))
    
    return {
        'tool': 'binwalk',
        'result': result['success'],
        'output': result.get('stdout', ''),
        'error': result.get('error', ''),
        'extracted_files': extracted_files
    }

@app.route('/')
def index():
    return """
    <h1>hello, steg-analyzer!</h1>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)