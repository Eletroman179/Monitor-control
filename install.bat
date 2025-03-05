@echo off
:: Install dependencies from the requirements.txt file

:: Step 1: Check if Git is installed
echo Checking if Git is installed...
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...
    :: Download and install Git
    powershell -Command "Invoke-WebRequest 'https://github.com/git-for-windows/git/releases/download/v2.40.1.windows.1/Git-2.40.1-64-bit.exe' -OutFile 'git-installer.exe'"
    start /wait git-installer.exe /VERYSILENT /NORESTART
    del git-installer.exe
) else (
    echo Git is already installed.
)

:: Step 2: Check if Python is installed
echo Checking if Python is installed...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    :: Download and install Python
    powershell -Command "Invoke-WebRequest 'https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe' -OutFile 'python-installer.exe'"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
) else (
    echo Python is already installed.
)

:: Step 3: Install pip if it's not already installed
echo Installing pip...
python -m ensurepip --upgrade

:: Step 4: Upgrade pip to the latest version
echo Upgrading pip...
python -m pip install --upgrade pip

:: Step 5: Clone the repository
echo Cloning the repository from GitHub...
git clone https://github.com/Eletroman179/Monitor-control.git

:: Step 6: Change to the repository directory
cd Monitor-control

:: Step 7: Install dependencies from requirements.txt
echo Installing dependencies from requirements.txt...
pip install -r https://github.com/Eletroman179/Monitor-control/raw/main/requirements.txt

:: Step 8: Start the application
echo Starting the application...
python main.py

:: End
pause
