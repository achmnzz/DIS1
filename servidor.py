import json
import os
import numpy as np
import psutil
import matplotlib
import socket
import threading
import queue
import time

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from reconstrucoes import cgne, cgnr, calcular_ganho_sinal
from matplotlib import pyplot as plt

# Número máximo de threads simultâneas
MAX_WORKERS = 5

# limite de uso de RAM em %
MEMORY_THRESHOLD = 95

# Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(BASE_DIR, "Dados")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "Resultados")

# Fila para conexões pendentes
fila_conexoes = queue.Queue()
fila_monitoramento = []


# Utilizando Anti-Grain Geometry para não precisar de uma GUI (interface gráfica)
matplotlib.use('Agg')

# Cria a pasta de resultados caso não exista
os.makedirs(PASTA_RESULTADOS, exist_ok=True)


def monitorar_memoria():
    """Retorna True se o uso de memória estiver abaixo do limite"""
    uso_memoria = psutil.virtual_memory().percent
    return uso_memoria < MEMORY_THRESHOLD


def carregar_csv(caminho):
    return np.loadtxt(caminho, delimiter=',')


# Printar conteúdo da fila (endereços, por exemplo)
def mostrar_fila():
    print("[FILA ATUAL]:", [endereco for endereco in fila_monitoramento])


def executar_algoritmo(conexao, endereco):
    requisicao = receber_requisicao(conexao)
    conexao.close()

    usuario = requisicao['usuario']
    algoritmo = requisicao['algoritmo']
    arquivo_H = requisicao['arquivo_H']
    arquivo_g = requisicao['arquivo_g']
    valores_g = requisicao['valores_g']

    print(f"[PROCESSANDO {endereco}] Reconstrução recebida de {usuario} usando {algoritmo}...")

    H, g_gain =                         preparar_dados(arquivo_H, valores_g)
    imagem, iteracoes, inicio, fim =    reconstruir_imagem(H, g_gain, algoritmo, arquivo_H)
    resultado_path =                    salvar_imagem(imagem, usuario, algoritmo, arquivo_g)

    salvar_log(usuario, algoritmo, arquivo_H, arquivo_g, iteracoes, inicio, fim, len(imagem.flatten()), resultado_path)

    print(f"[PROCESSANDO {endereco}] Reconstrução concluída para {usuario}. Resultado salvo.")


def receber_requisicao(conexao):
    dados_recebidos = b""
    while True:
        parte = conexao.recv(4096)
        if not parte:
            break
        dados_recebidos += parte
    return json.loads(dados_recebidos.decode('utf-8'))


def preparar_dados(arquivo_H, valores_g):
    H = carregar_csv(os.path.join(PASTA_DADOS, arquivo_H))
    g = np.array(valores_g)
    g_gain = calcular_ganho_sinal(g).flatten()
    return H, g_gain


def reconstruir_imagem(H, g_gain, algoritmo, arquivo_H):
    inicio = datetime.now()
    if algoritmo == "cgne":
        f, erros, iteracoes = cgne(H, g_gain)
    else:
        f, erros, iteracoes = cgnr(H, g_gain)
    fim = datetime.now()

    lado = int(np.sqrt(len(f)))
    imagem = np.abs(f).reshape((lado, lado), order='F')
    if arquivo_H == "H-1.csv":
        if imagem.max() != 0:
            imagem /= imagem.max()
        imagem = np.log1p(imagem)
    if imagem.max() != 0:
        imagem /= imagem.max()

    return imagem, iteracoes, inicio, fim


def salvar_imagem(imagem, usuario, algoritmo, arquivo_g):
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(imagem, cmap='gray', vmin=0, vmax=1)

    resultado_path = os.path.join(
        PASTA_RESULTADOS,
        f"recon_{usuario}_{algoritmo}_{arquivo_g.replace('.csv', '')}.png"
    )

    plt.savefig(resultado_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return resultado_path


def salvar_log(usuario, algoritmo, arquivo_H, arquivo_g, iteracoes, inicio, fim, tamanho, resultado_path):
    log_json = {
        "usuario": usuario,
        "algoritmo": algoritmo,
        "arquivo_H": arquivo_H,
        "arquivo_g": arquivo_g,
        "iteracoes": iteracoes,
        "tempo_inicio": str(inicio),
        "tempo_fim": str(fim),
        "duracao_segundos": (fim - inicio).total_seconds(),
        "tamanho": tamanho,
        "cpu": psutil.cpu_percent(interval=0.1),
        "memoria": psutil.virtual_memory().percent,
        "arquivo_saida": resultado_path
    }

    log_path = os.path.join(PASTA_RESULTADOS, f"log_{usuario}_{arquivo_g.replace('.csv', '')}.json")
    with open(log_path, 'w') as log_file:
        json.dump(log_json, log_file, indent=2)


'''Método chamado pelo processo anterior a ser executado

Executa executar_algoritmo com os dados da requisição
'''


def tratar_cliente(conexao, endereco):
    try:
        print(f"[PROCESSANDO] Conexão de {endereco}")
        executar_algoritmo(conexao, endereco)
    except Exception as e:
        print(f"[ERRO] Erro ao processar {endereco}: {e}")
    finally:
        conexao.close()
        fila_monitoramento.remove(endereco)
        print(f"[FINALIZADO] Conexão de {endereco} encerrada")
        mostrar_fila()


'''Interface de processamento de fila

Todas as requisições feitas entram na fila "fila_conexoes", que são processadas 
nesse método.
'''


def processar_fila(executor):
    while True:

        while not monitorar_memoria():
            print(f"[MEMÓRIA] Alta utilização de RAM. Aguardando...")
            time.sleep(1)

        #Remove e retornam um item da fila
        conexao, endereco = fila_conexoes.get()

        # Cria uma nova thread (executando tratar_cliente) toda vez que um worker estiver livre
        executor.submit(tratar_cliente, conexao, endereco)

        # Indica que a tarefa chamada pelo método get() anteriormente enfileirada foi concluida 
        fila_conexoes.task_done()


def iniciar_servidor(host='localhost', porta=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((host, porta))
        servidor.listen()
        print(f"[SERVIDOR] Ouvindo em {host}:{porta}...")

        # Executor com limite de threads simultâneas
        executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

        # Inicia a thread que processa a fila
        threading.Thread(target=processar_fila, args=(executor,), daemon=True).start()

        while True:
            conexao, endereco = servidor.accept()
            print(f"[NOVA CONEXÃO] {endereco} conectou.")
            
            #Apenas adiciona na fila de processamento
            fila_conexoes.put((conexao, endereco))
            fila_monitoramento.append(endereco)

            mostrar_fila()


if __name__ == "__main__":
    iniciar_servidor()
