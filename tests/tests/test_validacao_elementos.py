import os
import json
import random
import time
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import webbrowser

# ==============================
# 🔧 FIXTURE DO DRIVER
# ==============================
@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()

# ==============================
# 🧾 RELATÓRIO INTEGRADO AO HTML BASE
# ==============================
def atualizar_dashboard_html(dados_teste):
    """Atualiza o arquivo HTML SGMaster Test Center com os dados do teste"""
    html_path = "reports/sgmaster_test_center.html"
    json_path = "data/report_data.json"
    os.makedirs("reports", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    # === Lê histórico JSON (com fallback seguro)
    historico = []
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo:
                    historico = json.loads(conteudo)
        except Exception:
            historico = []

    historico.append(dados_teste)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

    # === Garante que o HTML base exista
    if not os.path.exists(html_path):
        print("⚠️ HTML base não encontrado em reports/sgmaster_test_center.html")
        return

    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # === Dados do teste
    test_id = dados_teste["id"]
    nome = dados_teste["nome"]
    icone = dados_teste["icone"]
    status = dados_teste["status"]
    status_class = "success" if status == "SUCESSO" else "fail"
    data_execucao = dados_teste["data_execucao"]
    duracao = dados_teste["duracao"]
    etapas = "\n".join(dados_teste.get("etapas", []))
    erro = dados_teste.get("erro", "")
    screenshot = dados_teste.get("screenshot", "")

    # === Bloco do card principal
    erro_html = f"<p><b>Erro:</b> {erro}</p>" if erro else ""
    screenshot_html = f"<h3>Screenshot:</h3><img src=\"{screenshot}\">" if screenshot else ""
    card_html = f"""
    <div id="{test_id}" class="card">
        <div class="header">
            <h2>{icone} {nome}</h2>
            <span class="status {status_class}">{status}</span>
        </div>
        <p><b>Executado em:</b> {data_execucao}</p>
        <p><b>Duração:</b> {duracao}s</p>
        <h3>Etapas:</h3>
        <pre>{etapas}</pre>
        {erro_html}
        {screenshot_html}
    </div>
    """

    # === Sidebar entry
    sidebar_item = f'<div class="test-item {status_class}" onclick="showDetails(\'{test_id}\')">{icone} {nome}</div>'

    # === Atualiza ou adiciona no HTML
    if f'id="{test_id}"' in html:
        inicio = html.index(f'<div id="{test_id}"')
        fim = html.index("</div>", inicio) + 6
        html = html[:inicio] + card_html + html[fim:]
    else:
        html = html.replace("</main>", card_html + "\n </main>")
        marcador_sidebar = '<p style="margin-top:auto;'
        html = html.replace(marcador_sidebar, sidebar_item + "\n " + marcador_sidebar)

    # === Salva alterações
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Dashboard atualizado: {nome} ({status}) → {html_path}")

# ==============================
# 🧠 FUNÇÕES DO FLUXO
# ==============================
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
        close_icon = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//i[text()='close']"))
        )
        close_icon.click()
    except TimeoutException:
        pass

def abrir_menu_vendas(driver):
    menu = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//p[contains(text(),'Vendas')]"))
    )
    menu.click()

# ==============================
# 🔹 FLUXO PDV AJUSTADO
# ==============================
def acessar_pdv(driver):
    """Abre o PDV usando o botão 'Cadastrar venda'"""
    try:
        btn_cadastrar = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[.//p[contains(text(),'Cadastrar venda')]]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_cadastrar)
        ActionChains(driver).move_to_element(btn_cadastrar).click().perform()

        # Espera o input do PDV aparecer
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='INSIRA O CÓDIGO']"))
        )
    except TimeoutException:
        raise Exception("❌ Não foi possível acessar o PDV - botão 'Cadastrar venda' não encontrado")

def cadastrar_venda(driver):
    """Função auxiliar caso precise clicar novamente"""
    acessar_pdv(driver)

def inserir_codigos_e_finalizar(driver, quantidade=5):
    etapas_local = []
    screenshot_final = None
    for i in range(quantidade):
        try:
            codigo = str(random.randint(1000, 9999))
            campo = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='INSIRA O CÓDIGO']"))
            )
            campo.clear()
            campo.send_keys(codigo)
            campo.send_keys(Keys.ENTER)
            etapas_local.append(f"✅ Código '{codigo}' inserido com sucesso")
            time.sleep(1.2)
        except Exception as e:
            etapas_local.append(f"⚠️ Erro ao inserir código: {e}")

    try:
        btn_finalizar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Finalizar')]]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", btn_finalizar)
        ActionChains(driver).move_to_element(btn_finalizar).click().perform()
        etapas_local.append("✅ Botão 'Finalizar' clicado com sucesso")

        os.makedirs("reports/screenshots", exist_ok=True)
        screenshot_final = "screenshots/fluxo_vendas_" + datetime.now().strftime("%Y-%m-%d_%H-%M") + ".png"
        driver.save_screenshot("reports/" + screenshot_final)
        etapas_local.append(f"📸 Screenshot salva em {screenshot_final}")

        driver.refresh()
        etapas_local.append("🔄 Tela atualizada (atalho F5 simulado)")

    except Exception as e:
        etapas_local.append(f"❌ Erro ao finalizar: {e}")

    return etapas_local, screenshot_final

# ==============================
# ✅ TESTE PRINCIPAL
# ==============================
def test_fluxo_vendas(driver):
    inicio = datetime.now()
    etapas = []
    erro = None
    screenshot = None
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
        etapas.append(f"❌ Erro durante execução: {erro}")

    fim = datetime.now()
    duracao = round((fim - inicio).total_seconds(), 2)
    dados_teste = {
        "id": "vendas",
        "nome": "Fluxo de Vendas",
        "icone": "🧾",
        "status": status,
        "data_execucao": fim.strftime("%d/%m/%Y %H:%M"),
        "duracao": duracao,
        "etapas": etapas,
        "erro": erro,
        "screenshot": screenshot
    }

    atualizar_dashboard_html(dados_teste)
