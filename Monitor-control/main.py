from flask import Flask, render_template, request, jsonify, redirect
from functools import wraps
import pyautogui
import sys
import os
import io
import logging
import socket
import uuid
import platform
import re
import time

# Windows-specific imports
if platform.system() == "Windows":
    import win32api
    import win32con
    import win32gui
    import win32process

os.chdir(os.path.dirname(__file__))

app = Flask(__name__)

def remove_ansi_codes(text):
    # This pattern matches ANSI escape sequences
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

# Configure logging
logging.basicConfig(
    filename="Logs.log",  # Save logs to a file
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Custom Formatter that removes ANSI codes after formatting the log record
class RemoveAnsiFormatter(logging.Formatter):
    def format(self, record):
        formatted = super().format(record)
        return remove_ansi_codes(formatted)

# Apply the custom formatter to all handlers of the root logger
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    # Preserve the original format and datefmt if set; otherwise, use defaults.
    fmt = handler.formatter._fmt if handler.formatter else "%(asctime)s - %(levelname)s - %(message)s"
    datefmt = handler.formatter.datefmt if handler.formatter and hasattr(handler.formatter, 'datefmt') else None
    handler.setFormatter(RemoveAnsiFormatter(fmt, datefmt))

# Also apply the formatter to the Werkzeug logger (used by Flask for request logs)
werkzeug_logger = logging.getLogger('werkzeug')
for handler in werkzeug_logger.handlers:
    fmt = handler.formatter._fmt if handler.formatter else "%(asctime)s - %(levelname)s - %(message)s"
    datefmt = handler.formatter.datefmt if handler.formatter and hasattr(handler.formatter, 'datefmt') else None
    handler.setFormatter(RemoveAnsiFormatter(fmt, datefmt))

# Redirect stdout and stderr to logging
class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ""
        
    def write(self, message):
        if isinstance(message, bytes):
            message = message.decode("utf-8", "ignore")
        if message.strip():
            self.logger.log(self.level, remove_ansi_codes(message).strip())
            
    def flush(self):
        pass

sys.stdout = StreamToLogger(logging.getLogger(), logging.INFO)
sys.stderr = StreamToLogger(logging.getLogger(), logging.ERROR)

def log_func(func):
    @wraps(func)  # Ensure the original function name and signature are preserved
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logging.info(f"Starting function: {func.__name__}()")
        
        # Call the function
        result = func(*args, **kwargs)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        logging.info(f"Function: {func.__name__}() completed in {elapsed_time:.4f} seconds.")
        
        return result
    return wrapper

@log_func
def egg():
    print("You found this cool good! this is a def called egg()")

@log_func
def wait(stop):
    time.sleep(stop)

@log_func
def clear_log():
    with open("Logs.log", "w") as file:
        file.write("")
    print("Log cleared.")

@log_func
def test():
    for i in range(10):
        print(i+1)
        time.sleep(0.1)

# Function to close the active window
@log_func
def close_active_window():
    """Closes the active window."""
    if platform.system() != "Windows":
        return "Functionality only available on Windows."

    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            h_process = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
            win32api.TerminateProcess(h_process, -1)
            win32api.CloseHandle(h_process)
            return "Active window closed successfully."
        else:
            return "No active window found."
    except Exception as e:
        logging.error(f"Error closing window: {e}")
        return f"Error: {e}"

# Shutdown function
@log_func
def shutdown():
    logging.info("Shutting down the system.")
    command = "shutdown /s /t 0" if platform.system() == "Windows" else "sudo shutdown now"
    os.system(command)
    return "The computer is shutting down."

# Reboot function
@log_func
def reboot():
    logging.info("Rebooting the system.")
    command = "shutdown /r /t 0" if platform.system() == "Windows" else "sudo reboot"
    os.system(command)
    return "The computer is rebooting."

# Alt + F4 function
@log_func
def F4():
    logging.info("Closing window using Alt + F4.")
    pyautogui.hotkey("alt", "F4")
    return "The active window has been closed."

# Retrieve IP address
@log_func
def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as e:
        logging.error(f"Error retrieving IP: {e}")
        return "Unknown IP"

# Retrieve MAC address
@log_func
def get_mac_address():
    try:
        mac = ":".join(["{:02x}".format((uuid.getnode() >> i) & 0xFF) for i in range(0, 2 * 6, 8)][::-1])
        return mac
    except Exception as e:
        logging.error(f"Error retrieving MAC address: {e}")
        return "Unknown MAC"

# Button configuration
button_functions = {
    "shutdown": shutdown,
    "reboot": reboot,
    "close_active_window": close_active_window,
}

buttons = [{"label": label.replace("_", " ").title(), "function": func} for label, func in button_functions.items()]

# Home route
@app.route("/")
def home():
    return render_template("index.html", buttons=buttons, ip=get_ip_address(), mac=get_mac_address())

# Route for executing button functions dynamically
@app.route("/run_button_function", methods=["POST"])
@log_func
def run_button_function():
    button_function = request.form.get("function")
    logging.info(f"Received function: {button_function}")

    func = button_functions.get(button_function)
    if func:
        result = func()
    else:
        result = "Unknown function."

    return jsonify({"message": result})

# Secure execution of Python code
@app.route("/run_code", methods=["POST"])
@log_func
def run_code():
    user_code = request.form.get("code", "")
    logging.info("User submitted Python code for execution.")

    # Redirect standard output to capture execution results
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        exec(user_code)  # Note: Be cautious with exec and consider security implications
        result = captured_output.getvalue()
    except Exception as e:
        result = f"Error: {e}"

    sys.stdout = sys.__stdout__  # Reset standard output
    return jsonify({"message": result})

# GitHub redirect
@app.route("/github")
def github():
    return redirect("https://github.com/Eletroman179/Monitor-control/")

# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Custom 404 page
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
