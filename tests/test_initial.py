# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import time

# def test_google_search(driver):
#     driver.get("https://www.google.com")
#     assert "Google" in driver.title

#     try:
#         accept_button = driver.find_element(By.XPATH, "//button[contains(text(),'Aceitar')]")
#         accept_button.click()
#     except:
#         pass

#     search_box = driver.find_element(By.NAME, "q")
#     search_box.send_keys("teste")
#     search_box.send_keys(Keys.RETURN)

#     time.sleep(2)  # Aguarda os resultados carregarem

#     assert "teste" in driver.page_source.lower()

#     # O navegador permanece aberto após o teste
