from flask import Flask, render_template, request, jsonify
import subprocess
import sys
import os
import glob
import shutil
import re
import json

app = Flask(__name__)

CONFIG_FILE = '/app/repopack.config.json'

class State:
    def __init__(self):
        self.repo_url = ""
        self.username = ""
        self.password = ""
        self.include_patterns = ""
        self.ignore_patterns = ""
        self.top_files_len = ""
        self.output_style = "plain"
        self.show_line_numbers = False
        self.verbose = False
        self.remove_comments = False
        self.remove_empty_lines = False
        self.cli_output = ""
        self.output = ""

state = State()

def hide_credentials(cli_output):
    pattern = r"(https?://)([^@]+)@"
    sanitized_output = re.sub(pattern, r"\1****:****@", cli_output)
    return sanitized_output

import os
import subprocess
import sys
import glob

def pack_repo():
    repo_url = state.repo_url
    if state.username and state.password:
        if repo_url.startswith("https://"):
            repo_url = f"https://{state.username}:{state.password}@{repo_url[8:]}"

    repopack_cmd = ["repopack", "--remote", repo_url]

    if state.include_patterns:
        repopack_cmd.extend(["--include", state.include_patterns])
    if state.ignore_patterns:
        repopack_cmd.extend(["--ignore", state.ignore_patterns])
    if state.top_files_len:
        repopack_cmd.extend(["--top-files-len", state.top_files_len])
    if state.output_style:
        repopack_cmd.extend(["--style", state.output_style])
    if state.show_line_numbers:
        repopack_cmd.append("--output-show-line-numbers")
    if state.remove_comments:
        repopack_cmd.append("--output-remove-comments")
    if state.remove_empty_lines:
        repopack_cmd.append("--output-remove-empty-lines")
    if state.verbose:
        repopack_cmd.append("--verbose")

    # Print the full command being executed
    print(f"Executing command: {' '.join(repopack_cmd)}", file=sys.stderr)

    try:
        process = subprocess.Popen(repopack_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        cli_output = ""
        for line in process.stdout:
            cli_output += line
            print(line, end='', file=sys.stderr)
        process.wait()
        state.cli_output = cli_output

        # Print the return code
        print(f"Repopack process returned with code: {process.returncode}", file=sys.stderr)

        # Search for the output file in multiple locations
        possible_locations = [
            "/app/repopack-output.txt",
            "/app/repopack-output.xml",
            "/app/repopack-output.md",
            "./repopack-output.txt",
            "./repopack-output.xml",
            "./repopack-output.md",
        ]

        output_file = None
        for location in possible_locations:
            if os.path.exists(location):
                output_file = location
                break

        if output_file:
            with open(output_file, 'r') as f:
                state.output = f.read()
            print(f"Found output file at: {output_file}", file=sys.stderr)
        else:
            state.output = "repopack-output file not found. Check the CLI output for details."
            print("Output file not found. Searched in:", file=sys.stderr)
            for location in possible_locations:
                print(f"  - {location}", file=sys.stderr)
            print("Current working directory:", os.getcwd(), file=sys.stderr)
            print("Files in current directory:", os.listdir(), file=sys.stderr)

        cleanup_files()
    except Exception as e:
        state.output = f"Error: {str(e)}"
        print(f"Exception occurred: {str(e)}", file=sys.stderr)

    return jsonify({
        'cli_output': hide_credentials(state.cli_output),
        'output': state.output
    })

def cleanup_files():
    for ext in ['txt', 'xml', 'md']:
        output_file = f"/app/repopack-output.{ext}"
        if os.path.exists(output_file):
            print(f"Removing file: {output_file}", file=sys.stderr)
            os.remove(output_file)

    for file in glob.glob("/tmp/repopack-*"):
        if os.path.isfile(file):
            print(f"Removing file: {file}", file=sys.stderr)
            os.remove(file)
        elif os.path.isdir(file):
            print(f"Removing directory: {file}", file=sys.stderr)
            shutil.rmtree(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pack', methods=['POST'])
def pack():
    state.repo_url = request.form.get('repo_url', '').strip()
    state.username = request.form.get('username', '').strip()
    state.password = request.form.get('password', '').strip()
    state.include_patterns = request.form.get('include_patterns', '').strip()
    state.ignore_patterns = request.form.get('ignore_patterns', '').strip()
    state.top_files_len = request.form.get('top_files_len', '').strip()
    state.output_style = request.form.get('output_style', 'plain')
    state.show_line_numbers = request.form.get('show_line_numbers') == 'true'
    state.remove_comments = request.form.get('remove_comments') == 'true'
    state.remove_empty_lines = request.form.get('remove_empty_lines') == 'true'
    state.verbose = request.form.get('verbose') == 'true'

    if not state.repo_url.endswith('.git'):
        return jsonify({'error': 'Repository URL must end with .git'})
    
    if not state.repo_url.startswith(('http://', 'https://')):
        return jsonify({'error': 'Repository URL must start with http:// or https://'})
    
    if state.top_files_len and not state.top_files_len.isdigit():
        return jsonify({'error': 'Top Files Length must be a positive integer'})

    return pack_repo()

@app.route('/get_config', methods=['GET'])
def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({})

@app.route('/update_config', methods=['POST'])
def update_config():
    new_config = request.json
    with open(CONFIG_FILE, 'w') as f:
        json.dump(new_config, f, indent=2)
    return jsonify({'message': 'Configuration updated successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=32123, debug=True)
