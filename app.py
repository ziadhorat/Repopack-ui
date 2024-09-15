import mesop as me
import subprocess
import sys
import os
import glob
import shutil
import re

@me.stateclass
class State:
    repo_url: str = ""
    username: str = ""
    password: str = ""
    include_patterns: str = ""
    ignore_patterns: str = ""
    top_files_len: str = ""
    output_style: str = "plain"
    show_line_numbers: bool = False
    verbose: bool = False
    cli_output: str = ""
    output: str = ""

def on_blur(e: me.InputBlurEvent, key: str):
    state = me.state(State)
    setattr(state, key, e.value)

def hide_credentials(cli_output):
    pattern = r"(https?://)([^@]+)@"
    sanitized_output = re.sub(pattern, r"\1****:****@", cli_output)
    return sanitized_output

def pack_repo(action: me.ClickEvent):
    state = me.state(State)
    
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
    yield

def cleanup_files():
    if os.path.exists("/app/repopack-output.txt"):
        os.remove("/app/repopack-output.txt")
    
    for file in glob.glob("/tmp/repopack-*"):
        if os.path.isfile(file):
            os.remove(file)
        elif os.path.isdir(file):
            shutil.rmtree(file)

@me.page(path="/")
def main():
    state = me.state(State)

    with me.box(style=me.Style(display="flex", flex_direction="column", align_items="center", margin=me.Margin(top=32))):
        me.text("Repopack", type="headline-4", style=me.Style(margin=me.Margin(bottom=16)))

        with me.box(style=me.Style(background="#e8eaf6", padding=me.Padding.all(16), border_radius="10px", width="80%", margin=me.Margin(bottom=32))):
            me.input(
                label="Repository URL",
                on_blur=lambda e: on_blur(e, 'repo_url'),
                style=me.Style(width="100%", font_size="12px", padding=me.Padding.all(10)),
                required=True
            )
            
            with me.box(style=me.Style(display="flex", gap="16px", width="100%")):
                me.input(
                    label="Username (optional)",
                    on_blur=lambda e: on_blur(e, 'username'),
                    style=me.Style(width="100%", font_size="12px", padding=me.Padding.all(10))
                )
                me.input(
                    label="Password (optional)",
                    type="password",
                    on_blur=lambda e: on_blur(e, 'password'),
                    style=me.Style(width="100%", font_size="12px", padding=me.Padding.all(10))
                )

            with me.box(style=me.Style(display="flex", gap="12px", width="100%")):
                me.input(
                    label="Include Patterns (optional, comma-separated)",
                    on_blur=lambda e: on_blur(e, 'include_patterns'),
                    style=me.Style(width="100%", font_size="16px", padding=me.Padding.all(10))
                )
                me.input(
                    label="Ignore Patterns (optional, comma-separated)",
                    on_blur=lambda e: on_blur(e, 'ignore_patterns'),
                    style=me.Style(width="100%", font_size="12px", padding=me.Padding.all(10))
                )
                me.input(
                    label="Top Files Length (optional)",
                    on_blur=lambda e: on_blur(e, 'top_files_len'),
                    style=me.Style(width="100%", font_size="12px", padding=me.Padding.all(10)),
                    placeholder="Enter a number"
                )
                
            me.checkbox(
                label="Show Line Numbers",
                on_change=lambda e: setattr(state, 'show_line_numbers', e.checked),
                checked=state.show_line_numbers,
                style=me.Style(width="100%")
            )

            me.text("Output Style", style=me.Style(margin=me.Margin(top=16)))
            me.radio(
                on_change=lambda e: setattr(state, 'output_style', e.value),
                options=[me.RadioOption(label="Plain", value="plain"), me.RadioOption(label="XML", value="xml")],
                value=state.output_style
            )

            me.checkbox(
                label="Verbose Logging",
                on_change=lambda e: setattr(state, 'verbose', e.checked),
                checked=state.verbose
            )

            me.button(
                "Pack Repository",
                on_click=pack_repo,
                style=me.Style(border_radius="20px", background="#4CAF50", color="#FFFFFF", height="40px", align_self="flex-end")
            )

        with me.box(style=me.Style(display="flex", gap="16px", width="80%", margin=me.Margin(top=32))):
            with me.box(style=me.Style(width="30%", background="#333333", padding=me.Padding.all(16), border_radius="10px")):
                me.text("CLI Output", type="headline-6", style=me.Style(color="#FFFFFF"))
                me.text(text=hide_credentials(state.cli_output), style=me.Style(white_space="pre-wrap", background="#333333", color="#FFFFFF"))

            with me.box(style=me.Style(width="70%", background="#f0f0f0", padding=me.Padding.all(16), border_radius="10px")):
                me.text("Repopack Output", type="headline-6")
                me.text(text=state.output, style=me.Style(white_space="pre-wrap"))

if __name__ == "__main__":
    me.app(main)

