import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
import shutil
import subprocess
import json

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'usbpdsecret'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    files = {}
    for fname in ['usb_pd_toc.jsonl', 'usb_pd_spec.jsonl', 'usb_pd_metadata.jsonl', 'validation_report.xlsx']:
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.exists(fpath):
            files[fname] = True
        else:
            files[fname] = False
    # Load ToC from usb_pd_spec.jsonl for display
    toc = []
    toc_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_spec.jsonl')
    if os.path.exists(toc_path):
        with open(toc_path, encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    toc.append(entry)
                except Exception:
                    continue
    return render_template('index.html', files=files, toc=toc)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = 'usb_pd_spec.pdf'
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # Run the main parser script
        result = subprocess.run(['python', 'main.py'], cwd=UPLOAD_FOLDER, capture_output=True, text=True)
        if result.returncode != 0:
            flash('Parsing failed: ' + result.stderr)
        else:
            flash('Parsing complete!')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type')
        return redirect(url_for('index'))
    

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
