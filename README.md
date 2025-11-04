pip install -r requirements.txt

python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

pytest --html=reports/report.html --self-contained-html
