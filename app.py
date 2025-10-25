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
        'error': result.get('stderr', ''),
        'extracted_files': extracted_files
    }

def analyze_with_foremost(filepath, output_dir):
    command = f"foremost -i {filepath} -o {output_dir}/foremost_output"
    result = run_command(command)

    recovered_files = []
    foremost_dir = os.path.join(output_dir, 'foremost_output')
    if os.path.exists(foremost_dir):
        for root, dirs, files in os.walk(foremost_dir):
            for file in files:
                if file != 'audit.txt':
                    recovered_files.append(os.path.join(root, file))

    return {
        'tool': 'foremost',
        'result': result['success'],
        'output': result.get('stdout', ''),
        'error': result.get('stderr', ''),
        'recovered_files': recovered_files
    }

def analyze_with_exiftool(filepath):
    command = f"exiftool {filepath}"
    result = run_command(command)

    return {
        'tool': 'exiftool',
        'result': result['success'],
        'metadata': result.get('stdout', ''),
        'error': result.get('stderr', '')
    }

def analyze_with_string(filepath):
    command = f"string {filepath}"
    result = run_command(command)

    strings_output = result.get('stdout', '')
    lines = strings_output.split('\n')[:1000] # might increase this, will see how it performs and then i will decide ig

    return {
        'tool': 'strings',
        'success': result['success'],
        'strings': '\n'.join(lines),
        'total_lines': len(strings_output.split('\n')),
        'error': result.get('stderr', '')
    }

def analyze_with_zsteg(filepath):
    command = f"zsteg {filepath}"
    result = run_command(command)

    return {
        'tool': 'zsteg',
        'success': result['success'],
        'output': result.get('stdout', ''),
        'error': result.get('stderr', '')
    }

@app.route('/')
def index():
    return """
    <h1>hello, steg-analyzer!</h1>
"""

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)