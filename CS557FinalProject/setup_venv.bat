@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Setup complete! Virtual environment is activated.
echo To activate the virtual environment in the future, run: venv\Scripts\activate.bat 