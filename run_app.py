import streamlit.web.cli as stcli
import os, sys

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        # 1. Identify the directory where the executable is located.
        # This is where you want data to persist.
        application_path = os.path.dirname(sys.executable)
        
        # Set an environment variable so your code knows where to save files
        os.environ['APP_ROOT'] = application_path

        # 2. Change directory to the PyInstaller temporary folder
        # so Streamlit can find 'app.py', 'pages/', 'assets/', etc.
        os.chdir(sys._MEIPASS)
    else:
        # In development, persistent dir is just the current folder
        os.environ['APP_ROOT'] = os.path.abspath(".")
    
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--global.developmentMode=false",
        "--browser.gatherUsageStats=false",
    ]
    sys.exit(stcli.main())