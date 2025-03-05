from flask import Flask, render_template, request, jsonify
import pyautogui
import sys
import os
import io
import win32api
import win32con
import win32gui
import win32process

app = Flask(__name__)

# Define the functions to run when buttons are clicked
def close_active_window():
    """Closes the active window while checking not_close rules"""
    try:
        active_window = gw.getActiveWindow()
        if not active_window:
            return  # No active window found

        window_title = active_window.title.lower()
        for app, behavior in not_close.items():
            if app in window_title:
                if behavior["use"]:
                    if behavior["action"] == "close":
                        hwnd = win32gui.GetForegroundWindow()
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        try:
                            h_process = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
                            win32api.TerminateProcess(h_process, -1)
                            win32api.CloseHandle(h_process)
                        except Exception:
                            pyautogui.hotkey("alt", "f4")
                    elif behavior["action"] == "shutdown":
                        os.system("shutdown /s /t 0")
                return

        # Default: Close other windows
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            h_process = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
            win32api.TerminateProcess(h_process, -1)
            win32api.CloseHandle(h_process)
        except Exception:
            os.system(f"taskkill /PID {pid} /F")

    except Exception:
        return  # Catch all other errors silently

def shutdown():
    print("shuting down")
    os.system("shutdown /s /t 0")
    return "The computer has been shut down!"

def reboot():
    print("rebooting")
    os.system("shutdown /r /t 0")
    return "The computer has been rebooted!"

def F4():
    print("Wow you saw this you like python? python web \033]8;;https://www.python.org/\033\\here\033]8;;\033\\ you found a easter egg!")
    pyautogui.hotkey('alt', 'F4')
    return "The window has been shutdown!"


# List of buttons and their corresponding functions
buttons = [
    {"label": "shutdown computer", "function": shutdown},
    {"label": "reboot computer", "function": reboot},
    {"label": "close window", "function": close_active_window}
]

# Route for the About page
@app.route('/about')
def about():
    return render_template('about.html')  # Your about page HTML

# Route for the homepage
@app.route("/")
def home():
    return render_template("index.html", buttons=buttons)

# Route to execute Python code
@app.route("/run_code", methods=["POST"])
def run_code():
    user_code = request.form['code']  # Get code from the textbox

    # Capture the output (stdout)
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        # Execute the user code
        exec(user_code)
        result = captured_output.getvalue()
    except Exception as e:
        result = f"Error: {e}"

    # Reset stdout
    sys.stdout = sys.__stdout__

    return jsonify({"message": result})

@app.route("/run_button_function", methods=["POST"])
def run_button_function():
    button_function = request.form['function']
    print(f"Received function: {button_function}")  # Debugging line
    
    if button_function == "def1":
        result = run_def1()
    elif button_function == "def2":
        result = run_def2()
    else:
        result = "Unknown function"
    
    return jsonify({"message": result})

# 404 Error page
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
