from flask import Flask, render_template, request, jsonify
from urllib.parse import urlparse, quote_plus
import subprocess
import sys
import os
import glob
import shutil
import re
import json
import requests

app = Flask(__name__)

CONFIG_FILE = '/app/repopack.config.json'

class State:
    def __init__(self):
        self.repo_url = ""
        self.username = ""
        self.password = ""
        self.branch = ""
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

def pack_repo():
    repo_url = state.repo_url
    if state.username and state.password:
        if repo_url.startswith("https://"):
            repo_url = f"https://{state.username}:{state.password}@{repo_url[8:]}"

    repopack_cmd = ["repopack", "--remote", repo_url]

    if state.branch:
        repopack_cmd.extend(["--branch", state.branch])
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

    try:
        process = subprocess.Popen(repopack_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        cli_output = ""
        for line in process.stdout:
            cli_output += line
            print(line, end='', file=sys.stderr)
        process.wait()
        state.cli_output = cli_output

        output_file = "/app/repopack-output.txt"
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                state.output = f.read()
        else:
            state.output = "repopack-output.txt not found. Check the terminal for details."

        cleanup_files()
    except Exception as e:
        state.output = f"Error: {str(e)}"

    return jsonify({
        'cli_output': hide_credentials(state.cli_output),
        'output': state.output
    })

def cleanup_files():
    for ext in ['txt', 'xml', 'md']:
        output_file = f"/app/repopack-output.{ext}"
        if os.path.exists(output_file):
            os.remove(output_file)

    for file in glob.glob("/tmp/repopack-*"):
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            shutil.rmtree(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pack', methods=['POST'])
def pack():
    state.repo_url = request.form.get('repo_url', '').strip()
    state.username = request.form.get('username', '').strip()
    state.password = request.form.get('password', '').strip()
    state.branch = request.form.get('branch', '').strip()
    state.include_patterns = request.form.get('include_patterns', '').strip()
    state.ignore_patterns = request.form.get('ignore_patterns', '').strip()
    state.top_files_len = request.form.get('top_files_len', '').strip()
    state.output_style = request.form.get('output_style', 'plain')
    state.show_line_numbers = request.form.get('show_line_numbers') == 'true'
    state.remove_comments = request.form.get('remove_comments') == 'true'
    state.remove_empty_lines = request.form.get('remove_empty_lines') == 'true'
    state.verbose = request.form.get('verbose') == 'true'

    # Server-side validation
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

import re
import base64
from urllib.parse import urlparse

@app.route('/get_branches', methods=['POST'])
def get_branches():
    repo_url = request.json.get('repo_url', '').strip()
    username = request.json.get('username', '')
    password = request.json.get('password', '')

    if not repo_url.endswith('.git'):
        return jsonify({'error': 'Invalid repository URL'})

    parsed_url = urlparse(repo_url)
    hostname = parsed_url.hostname

    if hostname == 'github.com':
        return get_github_branches(repo_url, username, password)
    elif hostname == 'gitlab.com':
        return get_gitlab_branches(repo_url, username, password)
    elif hostname == 'gitea.com':
        return get_gitea_branches(repo_url, username, password)
    else:
        # Handle self-hosted Git repositories
        return get_generic_git_branches(repo_url, username, password)

def get_generic_git_branches(repo_url, username, password):
    parsed_url = urlparse(repo_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Extract the project path
    path = parsed_url.path.strip('/').replace('.git', '')
    encoded_path = quote_plus(path)
    
    # Try GitLab API endpoint first
    gitlab_api_url = f"{base_url}/api/v4/projects/{encoded_path}/repository/branches"
    
    headers = {}
    if username and password:
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers['Authorization'] = f'Basic {auth}'
    
    try:
        response = requests.get(gitlab_api_url, headers=headers)
        response.raise_for_status()
        branches = [branch['name'] for branch in response.json()]
        return jsonify({'branches': branches})
    except requests.RequestException as gitlab_error:
        print(f"GitLab API error: {gitlab_error}")  # Debug print
        
        # If GitLab API fails, try generic API endpoints
        api_endpoints = [
            f"{base_url}/api/v1/repos/{path}/branches",  # Gitea-like
            f"{base_url}/api/repos/{path}/branches",  # Generic
        ]
        
        for endpoint in api_endpoints:
            try:
                response = requests.get(endpoint, headers=headers)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, list):
                    branches = [branch['name'] if isinstance(branch, dict) else branch for branch in data]
                    return jsonify({'branches': branches})
            except requests.RequestException as e:
                print(f"API endpoint error: {e}")  # Debug print
                continue
    
    return jsonify({'error': 'Unable to fetch branches. The repository might be private or the API is not supported.'})

def get_github_branches(repo_url, username, password):
    parts = re.search(r'github\.com[/:]([^/]+)/([^/.]+)', repo_url)
    if not parts:
        return jsonify({'error': 'Invalid GitHub repository URL'})
    
    owner, repo = parts.groups()
    api_url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    
    headers = {}
    if username and password:
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers['Authorization'] = f'Basic {auth}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        branches = [branch['name'] for branch in response.json()]
        return jsonify({'branches': branches})
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch branches: {str(e)}'})

def get_gitlab_branches(repo_url, username, password):
    parts = re.search(r'gitlab\.com[/:]([^/]+)/([^/.]+)', repo_url)
    if not parts:
        return jsonify({'error': 'Invalid GitLab repository URL'})
    
    owner, repo = parts.groups()
    api_url = f"https://gitlab.com/api/v4/projects/{owner}%2F{repo}/repository/branches"
    
    headers = {}
    if username and password:
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers['Authorization'] = f'Basic {auth}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        branches = [branch['name'] for branch in response.json()]
        return jsonify({'branches': branches})
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch branches: {str(e)}'})

def get_gitea_branches(repo_url, username, password):
    parts = re.search(r'gitea\.com[/:]([^/]+)/([^/.]+)', repo_url)
    if not parts:
        return jsonify({'error': 'Invalid Gitea repository URL'})
    
    owner, repo = parts.groups()
    api_url = f"https://gitea.com/api/v1/repos/{owner}/{repo}/branches"
    
    headers = {}
    if username and password:
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers['Authorization'] = f'Basic {auth}'

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        branches = [branch['name'] for branch in response.json()]
        return jsonify({'branches': branches})
    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch branches: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=32123, debug=True)
