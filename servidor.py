import socket
import threading
import json
import os
import numpy as np
from datetime import datetime
import psutil
from reconstrucoes import cgne, cgnr

PASTA_DADOS = ".\Dados"
PASTA_RESULTADOS = ".\Resultados"
os.makedirs(PASTA_RESULTADOS, exist_ok=True)


def carregar_csv(caminho):
    return np.loadtxt(caminho, delimiter=',')


def calcular_ganho_sinal(g):
    g = np.atleast_2d(g)
    if g.shape[0] == 1:
        g = g.T
    S, N = g.shape
    ganho = np.array([100 + (1/20) * (l+1)**1.5 for l in range(S)]).reshape(S, 1)
    return g * ganho


def tratar_cliente(conexao, endereco):
    dados_recebidos = conexao.recv(8192).decode('utf-8')
    requisicao = json.loads(dados_recebidos)
    usuario = requisicao['usuario']
    algoritmo = requisicao['algoritmo']
    arquivo_H = requisicao['arquivo_H']
    arquivo_g = requisicao['arquivo_g']

    print(f"Reconstrução recebida de {usuario} usando {algoritmo}...")

    H = carregar_csv(os.path.join(PASTA_DADOS, arquivo_H))
    g = carregar_csv(os.path.join(PASTA_DADOS, arquivo_g))
    g_gain = calcular_ganho_sinal(g).flatten()

    inicio = datetime.now()

    if algoritmo == "cgne":
        f, erros, iteracoes = cgne(H, g_gain)
    else:
        f, erros, iteracoes = cgnr(H, g_gain)

    fim = datetime.now()

    resultado_path = os.path.join(PASTA_RESULTADOS, f"recon_{usuario}_{algoritmo}_{arquivo_g}.csv")
    np.savetxt(resultado_path, f, delimiter=',')

    log_info = {
        "usuario": usuario,
        "algoritmo": algoritmo,
        "arquivo_H": arquivo_H,
        "arquivo_g": arquivo_g,
        "iteracoes": iteracoes,
        "tempo_inicio": str(inicio),
        "tempo_fim": str(fim),
        "duracao_segundos": (fim - inicio).total_seconds(),
        "tamanho": len(f),
        "cpu": psutil.cpu_percent(interval=0.1),
        "memoria": psutil.virtual_memory().percent,
        "arquivo_saida": resultado_path
    }

    with open(os.path.join(PASTA_RESULTADOS, f"log_{usuario}_{arquivo_g}.json"), 'w') as log_file:
        json.dump(log_info, log_file, indent=2)

    print(f"Reconstrução concluída para {usuario}. Resultado salvo.")
    conexao.close()


def iniciar_servidor(host='localhost', porta=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((host, porta))
        servidor.listen()
        print(f"Servidor ouvindo em {host}:{porta}...")

        while True:
            conexao, endereco = servidor.accept()
            thread = threading.Thread(target=tratar_cliente, args=(conexao, endereco))
            thread.start()


if __name__ == "__main__":
    iniciar_servidor()
