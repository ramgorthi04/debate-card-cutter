from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from cutter import *
from research import *  
from scraper import * 

app = Flask(__name__)
# Set the upload folder to the current working directory
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        n = int(request.form['n'])
        
        file_paths = generate_docs(user_input, n)
        
        return render_template('index.html', files=file_paths, arg=user_input)
    
    return render_template('index.html')

def generate_docs(argument: str, num_cards: int) -> list[str]:
    """Returns filepath of generated files"""
    sources_and_tags = get_sources(argument, num_cards)
    
    if sources_and_tags == {}: # re-try once
        sources_and_tags = get_sources(argument)
        if sources_and_tags == {}:
            return []
    
    filepaths = []
    for source, tag in sources_and_tags.items():
        filepath = cut_card(tag, source)
        if filepath is not None:
            # Ensure the filepath is relative to the UPLOAD_FOLDER
            filepaths.append(os.path.relpath(filepath, app.config['UPLOAD_FOLDER']))
            print(f"Generated file: {filepath}")
    return filepaths

@app.route('/logs')
def logs():
    def generate():
        with open('logs/output.log', 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                yield f"data:{line}\n\n"
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/download/<path:filename>')
def download_file(filename):
    # Ensure the path is correct and debug print the path
    try:
        print(f"Attempting to send file: {filename}")
        full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Full path: {full_path}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5000, debug=True)