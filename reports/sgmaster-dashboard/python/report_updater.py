import os
import json
import time
import random
import webbrowser
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ==============================================================
# 🔧 FIXTURE DO DRIVER
# ==============================================================
@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()


# ==============================================================
# 🧾 ATUALIZA O DASHBOARD (index.html)
# ==============================================================
def atualizar_dashboard_html(dados_teste):
    """
    Atualiza o dashboard moderno (index.html) dentro de reports/sgmaster-dashboard.
    Também mantém histórico em data/results.json.
    """

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /reports/sgmaster-dashboard
    JSON_PATH = os.path.join(BASE_DIR, "data", "results.json")
    HTML_PATH = os.path.join(BASE_DIR, "index.html")

    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    # === Lê histórico existente
    historico = []
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo:
                    historico = json.loads(conteudo)
        except Exception:
            historico = []

    # === Adiciona novo teste
    historico.append(dados_teste)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

    print(f"✅ JSON atualizado com {len(historico)} registros → {JSON_PATH}")

    # === Abre o dashboard automaticamente
    if os.path.exists(HTML_PATH):
        full_path = os.path.abspath(HTML_PATH)
        webbrowser.open(f"file:///{full_path}")
        print(f"📊 Dashboard aberto: {full_path}")
    else:
        print(f"⚠️ Dashboard não encontrado em {HTML_PATH}")


# ==============================================================
# 🧠 FUNÇÕES DO FLUXO DE TESTE
# ==============================================================
def login(driver):
    driver.get("https://hom.sgmaster.com.br/empresas")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "username"))
    ).send_keys("devalexbruno@gmail.com")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "password"))
    ).send_keys("tanna2810")

    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "kc-login"))
    ).click()


def acessar_empresa_direto(driver, url_empresa):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    driver.get(url_empresa)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))


def fechar_modal(driver):
    try:
        close_icon = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//i[text()='close']")))
        close_icon.click()
    except TimeoutException:
        pass


def abrir_menu_vendas(driver):
    menu = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(),'Vendas')]")))
    menu.click()


def acessar_pdv(driver):
    pdv_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/vendas/pdv')]")))
    pdv_link.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))


def cadastrar_venda(driver):
    cadastrar_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(),'Cadastrar venda')]")))
    cadastrar_btn.click()


def inserir_codigos_e_finalizar(driver, quantidade=5):
    etapas_local = []

    for i in range(quantidade):
        try:
            codigo = str(random.randint(1000, 9999))
            campo = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='INSIRA O CÓDIGO']")))
            campo.clear()
            campo.send_keys(codigo)
            campo.send_keys(Keys.ENTER)
            etapas_local.append(f"✅ Código '{codigo}' inserido com sucesso")
            time.sleep(1)
        except Exception as e:
            etapas_local.append(f"⚠️ Erro ao inserir código: {e}")

    try:
        btn_finalizar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Finalizar')]]")))
        btn_finalizar.click()
        etapas_local.append("✅ Botão 'Finalizar' clicado com sucesso")

        os.makedirs(os.path.join("reports", "screenshots"), exist_ok=True)
        screenshot_final = os.path.join("reports", "screenshots", f"fluxo_vendas_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.png")
        driver.save_screenshot(screenshot_final)
        etapas_local.append(f"📸 Screenshot salva em {screenshot_final}")

        driver.refresh()
        etapas_local.append("🔄 Tela atualizada")

    except Exception as e:
        etapas_local.append(f"❌ Erro ao finalizar: {e}")
        screenshot_final = None

    return etapas_local, screenshot_final


# ==============================================================
# ✅ TESTE PRINCIPAL
# ==============================================================
def test_fluxo_vendas(driver):
    inicio = datetime.now()
    etapas = []
    erro = None

    try:
        login(driver)
        etapas.append("✅ Login realizado com sucesso")

        acessar_empresa_direto(driver, "https://testejcs.hom.sgmaster.com.br")
        etapas.append("✅ Empresa acessada com sucesso")

        fechar_modal(driver)
        etapas.append("✅ Modal fechado (se existia)")

        abrir_menu_vendas(driver)
        etapas.append("✅ Menu 'Vendas' aberto")

        acessar_pdv(driver)
        etapas.append("✅ Tela de PDV acessada")

        cadastrar_venda(driver)
        etapas.append("✅ Clicou em 'Cadastrar venda'")

        etapas_codigos, screenshot = inserir_codigos_e_finalizar(driver, quantidade=5)
        etapas.extend(etapas_codigos)

        status = "SUCESSO"

    except Exception as e:
        erro = str(e)
        status = "FALHA"
        screenshot = None
        etapas.append(f"❌ Erro durante execução: {erro}")

    fim = datetime.now()
    duracao = round((fim - inicio).total_seconds(), 2)

    dados_teste = {
        "id": f"vendas_{int(time.time())}",
        "nome": "Fluxo de Vendas",
        "icone": "🧾",
        "status": status,
        "data_execucao": fim.strftime("%d/%m/%Y %H:%M"),
        "duracao": duracao,
        "etapas": etapas,
        "erro": erro,
        "screenshot": screenshot.replace("\\", "/") if screenshot else None
    }

    atualizar_dashboard_html(dados_teste)
    assert status == "SUCESSO", f"Teste falhou: {erro}"
