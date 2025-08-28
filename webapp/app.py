"""
Flask web application for USB PD document parsing and viewing.
"""
import os
import sys
import json
import logging
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash, jsonify
import shutil
import subprocess

# Add parent directory to path to import from main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import USBPDParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.secret_key = 'usbpdsecret123'

def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render main page."""
    # Check for output files
    files = {}
    for fname in ['usb_pd_toc.jsonl', 'usb_pd_spec.jsonl', 'usb_pd_metadata.jsonl', 'validation_report.xlsx']:
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        files[fname] = os.path.exists(fpath)
    
    # Get processing status
    pdf_exists = os.path.exists(os.path.join(UPLOAD_FOLDER, 'usb_pd_spec.pdf'))
    
    # Get statistics
    stats = get_parsing_stats()
    
    # Load ToC for display
    toc = []
    toc_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_toc.jsonl')
    if os.path.exists(toc_path):
        try:
            with open(toc_path, encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line)
                    toc.append(entry)
        except Exception as e:
            logger.error(f"Error loading ToC: {str(e)}")
    
    return render_template('index.html', 
                         files=files, 
                         toc=toc, 
                         pdf_exists=pdf_exists,
                         stats=stats)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF upload."""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = 'usb_pd_spec.pdf'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            flash(f'Uploaded {file.filename} successfully')
            
            # Process the PDF
            parser = USBPDParser(filepath, UPLOAD_FOLDER)
            parser.run()
            
            flash('PDF processed successfully!')
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            flash(f'Error processing PDF: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files."""
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/api/stats')
def get_stats_api():
    """API endpoint for parsing statistics."""
    return jsonify(get_parsing_stats())

@app.route('/api/sections')
def get_sections_api():
    """API endpoint for sections data."""
    section_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_spec.jsonl')
    sections = []
    
    if os.path.exists(section_path):
        try:
            with open(section_path, encoding='utf-8') as f:
                for line in f:
                    sections.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error loading sections: {str(e)}")
    
    return jsonify(sections)

@app.route('/view/<section_id>')
def view_section(section_id):
    """View specific section content."""
    section_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_spec.jsonl')
    section = None
    
    if os.path.exists(section_path):
        try:
            with open(section_path, encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    if data.get('section_id') == section_id:
                        section = data
                        break
        except Exception as e:
            logger.error(f"Error finding section {section_id}: {str(e)}")
    
    if not section:
        flash(f'Section {section_id} not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('section.html', section=section)

def get_parsing_stats():
    """Get statistics about the parsing results."""
    stats = {
        'toc_count': 0,
        'section_count': 0,
        'coverage': 0,
        'metadata': {}
    }
    
    # Get ToC count
    toc_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_toc.jsonl')
    if os.path.exists(toc_path):
        try:
            with open(toc_path, encoding='utf-8') as f:
                stats['toc_count'] = sum(1 for _ in f)
        except Exception:
            pass
    
    # Get section count
    section_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_spec.jsonl')
    if os.path.exists(section_path):
        try:
            with open(section_path, encoding='utf-8') as f:
                stats['section_count'] = sum(1 for _ in f)
        except Exception:
            pass
    
    # Calculate coverage
    if stats['toc_count'] > 0:
        stats['coverage'] = (stats['section_count'] / stats['toc_count']) * 100
    
    # Get metadata
    metadata_path = os.path.join(UPLOAD_FOLDER, 'usb_pd_metadata.jsonl')
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, encoding='utf-8') as f:
                stats['metadata'] = json.loads(f.readline())
        except Exception:
            pass
    
    return stats

if __name__ == '__main__':
    app.run(debug=True)
