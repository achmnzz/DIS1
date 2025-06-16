import socket
import json
import random
import numpy as np
import time
import psutil
from pathlib import Path
from datetime import datetime

# Configurações
PASTA_DADOS = Path(__file__).parent.resolve() / "Dados"
PASTA_RESULTADOS = Path(__file__).parent.resolve() /  "Resultados"

NUM_REQUISICOES = 10
INTERVALO_MIN = 1  # segundos
INTERVALO_MAX = 3  # segundos

host = 'localhost'
porta = 5000

# Monitoramento de desempenho
memorias = []
cpus = []
inicio = datetime.now()

for i in range(NUM_REQUISICOES):
    usuario = f"usuario_{random.randint(1, 100)}"
    algoritmo = random.choice(["cgne", "cgnr"])
    arquivo_H = random.choice(["H-1.csv", "H-2.csv"])

    if arquivo_H == "H-1.csv":
        arquivo_g = random.choice(["g-60x60-1.csv", "g-60x60-2.csv", "A-60x60-1.csv"])
    else:
        arquivo_g = random.choice(["g-30x30-1.csv", "g-30x30-2.csv", "A-30x30-1.csv"])

    g_path = PASTA_DADOS / arquivo_g
    g_valores = np.loadtxt(g_path, delimiter=',').tolist()

    mensagem = {
        "usuario": usuario,
        "algoritmo": algoritmo,
        "arquivo_H": arquivo_H,
        "arquivo_g": arquivo_g,
        "valores_g": g_valores
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((host, porta))
            cliente.sendall(json.dumps(mensagem).encode('utf-8'))
        print(f"[{i+1}/{NUM_REQUISICOES}] Requisição enviada ({arquivo_g})")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar requisição: {e}")

    # Registrar uso de recursos locais
    cpus.append(psutil.cpu_percent(interval=0.1))
    memorias.append(psutil.virtual_memory().percent)

    # Espera aleatória entre envios
    time.sleep(random.uniform(INTERVALO_MIN, INTERVALO_MAX))

# Geração do relatório
fim = datetime.now()
relatorio = {
    "envios": NUM_REQUISICOES,
    "inicio": str(inicio),
    "fim": str(fim),
    "duracao_segundos": (fim - inicio).total_seconds(),
    "cpu_medio": round(sum(cpus) / len(cpus), 2),
    "memoria_media": round(sum(memorias) / len(memorias), 2),
    "uso_cpu": cpus,
    "uso_memoria": memorias
}

relatorio_path = PASTA_RESULTADOS / f"relatorio_desempenho.json"
with open(relatorio_path, 'w') as f:
    json.dump(relatorio, f, indent=2)

print(f"[RELATÓRIO] Salvo em: {relatorio_path}")

