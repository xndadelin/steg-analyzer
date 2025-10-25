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
    command = f"binwalk --extract --directory={output_dir} {filepath}"
    result = run_command(command)

    extracted_files = []
    if os.path.exists(output_dir):
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                extracted_files.append(os.path.join(root, file))
    
    return {
        'tool': 'binwalk',
        'success': result['success'],
        'output': result.get('stdout', ''),
        'error': result.get('stderr', ''),
        'extracted_files': extracted_files
    }

def analyze_with_foremost(filepath, output_dir):
    command = f"foremost -i {filepath} -o {output_dir}/foremost_output"
    result = run_command(command)

    recovered_files = []
    audit_file = os.path.join(output_dir, 'foremost_output', 'audit.txt')
    foremost_dir = os.path.join(output_dir, 'foremost_output')
    if os.path.exists(foremost_dir):
        for root, dirs, files in os.walk(foremost_dir):
            for file in files:
                if file != 'audit.txt':
                    recovered_files.append(os.path.join(root, file))

    content_of_audit = ''
    if os.path.exists(audit_file):
        with open(audit_file, 'r') as f:
            content_of_audit = f.read()

    return {
        'tool': 'foremost',
        'success': result['success'],
        'output': content_of_audit,
        'error': '' if 'Processing' in result.get('stderr', '') else result.get('stderr', ''),
        'recovered_files': recovered_files
    }

def analyze_with_exiftool(filepath):
    command = f"exiftool {filepath}"
    result = run_command(command)

    return {
        'tool': 'exiftool',
        'success': result['success'],
        'metadata': result.get('stdout', ''),
        'error': result.get('stderr', '')
    }

def analyze_with_string(filepath):
    command = f"strings {filepath}"
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

# to do: figure out how to install stegoveritas :skull: without pip3

def analyze_with_pngcheck(filepath):
    command = f"pngcheck {filepath}"
    result = run_command(command)

    return {
        'tool': 'pngcheck',
        'success': result['success'],
        'output': result.get('stdout', ''),
        'error': result.get('stderr', '')
    }

def apply_image_filters(filepath, output_dir):
    filters_applied = {}

    try:
        img = Image.open(filepath)

        grayscale = img.convert('L')
        gray_path = os.path.join(output_dir, 'filter_grayscale.png')
        grayscale.save(gray_path)
        filters_applied['grayscale'] = gray_path

        enhancer = ImageEnhance.Contrast(img)
        high_contrast = enhancer.enhance(3.0)
        contrast_path = os.path.join(output_dir, 'filter_high_contrast.png')
        high_contrast.save(contrast_path)
        filters_applied['high_contrast'] = contrast_path

        edges = img.filter(ImageFilter.FIND_EDGES)
        edges_path = os.path.join(output_dir, 'filter_edges.png')
        edges.save(edges_path)
        filters_applied['edges'] = edges_path

        brightness = ImageEnhance.Brightness(img)
        bright = brightness.enhance(2.0)
        bright_path = os.path.join(output_dir, 'filter_brightness.png')
        bright.save(bright_path)
        filters_applied['brightness'] = bright_path

        if img.mode == 'RGB':
            inverted = Image.eval(img, lambda x: 255 - x)
            inverted_path = os.path.join(output_dir, 'filter_inverted.png')
            inverted.save(inverted_path)
            filters_applied['inverted'] = inverted_path
    
    except Exception as e:
        filters_applied['error'] = str(e)

    return filters_applied


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'no file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'no selected file'}), 400
    
    if file and allowed_file(file.filename):
        analysis_id = str(uuid.uuid4())

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{analysis_id}_{filename}")
        file.save(filepath)

        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], analysis_id)
        os.makedirs(output_dir, exist_ok=True)

        file_type = get_file_type(filepath)
        file_ext = filename.rsplit('.', 1)[1].lower()

        results = {
            'analysis_id': analysis_id,
            'filename': filename,
            'file_type': file_type,
            'file_extension': file_ext,
            'analyses': []
        }

        results['analyses'].append(analyze_with_exiftool(filepath))
        results['analyses'].append(analyze_with_string(filepath))
        results['analyses'].append(analyze_with_binwalk(filepath, output_dir))
        results['analyses'].append(analyze_with_foremost(filepath, output_dir))

        if file_ext in ['png']:
            results['analyses'].append(analyze_with_zsteg(filepath))
            results['analyses'].append(analyze_with_pngcheck(filepath))

        if file_ext in ['bmp']:
            results['analyses'].append(analyze_with_zsteg(filepath))

        filters = apply_image_filters(filepath, output_dir)
        results['filters'] = filters

        return jsonify(results)
    
    return jsonify({'error': 'file type not allowed'}), 400

@app.route('/download/<analysis_id>/<path:filename>')
def download_file(analysis_id, filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], analysis_id, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    
    return "File not found", 404

@app.route('/filter/<analysis_id>/<filter_name>')
def get_filter(analysis_id, filter_name):
    filter_path = os.path.join(app.config['OUTPUT_FOLDER'], analysis_id, f'filter_{filter_name}.png')
    if os.path.exists(filter_path):
        return send_file(filter_path, as_attachment=True)

    return "Filter not found", 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)