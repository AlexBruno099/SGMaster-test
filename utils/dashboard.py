import os
import json
import webbrowser
from datetime import datetime

def atualizar_dashboard_html(dados_teste):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    JSON_PATH = os.path.join(BASE_DIR, "data", "results.json")
    HTML_PATH = os.path.join(BASE_DIR, "reports", "sgmaster-dashboard", "index.html")

    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    historico = []
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                conteudo = f.read().strip()
                if conteudo:
                    historico = json.loads(conteudo)
        except Exception:
            historico = []

    historico.append(dados_teste)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)

    print(f"✅ JSON atualizado com {len(historico)} registros → {JSON_PATH}")

    if os.path.exists(HTML_PATH):
        full_path = os.path.abspath(HTML_PATH)
        webbrowser.open(f"file:///{full_path}")
        print(f"📊 Dashboard aberto: {full_path}")
    else:
        print(f"⚠️ Dashboard não encontrado em {HTML_PATH}")
