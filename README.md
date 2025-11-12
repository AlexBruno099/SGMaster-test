pip install -r requirements.txt

python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

python run_tests.py

pdb.set_trace()


<!-- Usar Atalhos -->
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

ActionChains(driver).send_keys(Keys.F5).perform()
