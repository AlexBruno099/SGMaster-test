import os
import json
import webbrowser
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.dashboard import atualizar_dashboard_html

def pytest_runtest_makereport(item, call):
    if call.when == "call":
        outcome = "SUCESSO" if call.excinfo is None else "FALHA"
        dados_teste = {
            "id": f"{item.name}_{int(datetime.now().timestamp())}",
            "nome": item.name.replace("_", " ").title(),
            "icone": "🧪",
            "status": outcome,
            "data_execucao": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "duracao": round(call.stop - call.start, 2),
            "etapas": [f"Teste '{item.name}' executado automaticamente"],
            "erro": str(call.excinfo.value) if call.excinfo else None,
            "screenshot": None  # você pode capturar aqui se quiser
        }

        atualizar_dashboard_html(dados_teste)
