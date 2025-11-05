import os
import subprocess

TESTS_DIR = "tests"

def listar_testes():
    print("\n📂 Testes disponíveis:\n")
    arquivos = []
    for root, _, files in os.walk(TESTS_DIR):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                caminho = os.path.join(root, file)
                arquivos.append(caminho)
    for i, caminho in enumerate(arquivos):
        print(f"[{i}] {caminho}")
    return arquivos

def executar_teste(caminho):
    print(f"\n🚀 Executando: {caminho}\n")
    subprocess.run(["pytest", caminho])

if __name__ == "__main__":
    testes = listar_testes()
    escolha = input("\nDigite o número do teste que deseja rodar: ")
    if escolha.isdigit() and int(escolha) < len(testes):
        executar_teste(testes[int(escolha)])
    else:
        print("❌ Escolha inválida.")
