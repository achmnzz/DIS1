import socket
import threading
import json
import os
import numpy as np
from datetime import datetime
import psutil
from reconstrucoes import cgne, cgnr, calcular_ganho_sinal
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg')

PASTA_DADOS = "./Dados"
PASTA_RESULTADOS = "./Resultados"
os.makedirs(PASTA_RESULTADOS, exist_ok=True)


def carregar_csv(caminho):
    return np.loadtxt(caminho, delimiter=',')


def tratar_cliente(conexao, endereco):
    dados_recebidos = b""
    while True:
        parte = conexao.recv(4096)
        if not parte:
            break
        dados_recebidos += parte
    requisicao = json.loads(dados_recebidos.decode('utf-8'))
    conexao.close()
    usuario = requisicao['usuario']
    algoritmo = requisicao['algoritmo']
    arquivo_H = requisicao['arquivo_H']
    arquivo_g = requisicao['arquivo_g']
    valores_g = requisicao['valores_g']

    print(f"Reconstrução recebida de {usuario} usando {algoritmo}...")

    H = carregar_csv(os.path.join(PASTA_DADOS, arquivo_H))
    g = np.array(valores_g)
    g_gain = calcular_ganho_sinal(g).flatten()

    inicio = datetime.now()

    if algoritmo == "cgne":
        f, erros, iteracoes = cgne(H, g_gain)
    else:
        f, erros, iteracoes = cgnr(H, g_gain)

    fim = datetime.now()

    lado = int(np.sqrt(len(f)))
    imagem = f.reshape((lado, lado))
    imagem -= imagem.min()
    if imagem.max() != 0:
        imagem /= imagem.max()

    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(imagem, cmap='gray', vmin=0, vmax=1)

    resultado_path = os.path.join(PASTA_RESULTADOS, f"recon_{usuario}_{algoritmo}_{arquivo_g.replace('.csv','')}.png")
    plt.savefig(resultado_path, bbox_inches='tight', pad_inches=0)
    plt.close()

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

    with open(os.path.join(PASTA_RESULTADOS, f"log_{usuario}_{arquivo_g.replace('.csv','')}.json"), 'w') as log_file:
        json.dump(log_info, log_file, indent=2)

    print(f"Reconstrução concluída para {usuario}. Resultado salvo.")


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
