import asyncio
import json
import uuid
import numpy as np
import psutil
import logging
import matplotlib

from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from matplotlib import pyplot as plt
from pydantic import BaseModel
from reconstrucoes import cgne, cgnr, calcular_ganho_sinal

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("servidor")

# Diretórios
BASE_DIR = Path(__file__).resolve().parent
PASTA_DADOS = BASE_DIR / "Dados"
PASTA_RESULTADOS = BASE_DIR / "Resultados"

# Cria a pasta de resultados caso não exista
PASTA_RESULTADOS.mkdir(exist_ok=True)

# Fila de jobs
requisicoes = asyncio.Queue()

# Status dos jobs
jobs = {}

# Memória limite
MEMORY_THRESHOLD = 90
MAX_WORKERS = 8

# Utilizando Anti-Grain Geometry para não precisar de uma GUI (interface gráfica)
matplotlib.use('Agg')


# Modelo da requisição
class RequisicaoReconstrucao(BaseModel):
    usuario: str
    algoritmo: str
    arquivo_H: str
    arquivo_g: str
    valores_g: list[float]


# Função de processamento pesado
def aguardar_memoria(job_id):
    while not monitorar_memoria():
        uso = psutil.virtual_memory().percent
        logger.info(f"[{job_id}] Memória alta ({uso}%). Aguardando...")
        import time
        time.sleep(1)


def carregar_dados(dados):
    H = np.loadtxt(PASTA_DADOS / dados.arquivo_H, delimiter=",", dtype=np.float64)
    g = np.array(dados.valores_g, dtype=np.float64)
    g_gain = calcular_ganho_sinal(g).flatten().astype(np.float64)
    return H, g_gain


def reconstruir_imagem(H, g_gain, algoritmo):
    if algoritmo == "cgne":
        f, erros, iteracoes = cgne(H, g_gain)
    else:
        f, erros, iteracoes = cgnr(H, g_gain)
    return f, iteracoes


def processar_imagem(f, arquivo_H):
    lado = int(np.sqrt(len(f)))
    imagem = np.abs(f).reshape((lado, lado), order='F')
    if arquivo_H == "H-1.csv":
        if imagem.max() != 0:
            imagem /= imagem.max()
        imagem = np.log1p(imagem)
    if imagem.max() != 0:
        imagem /= imagem.max()

    return imagem


def salvar_imagem(imagem, dados):
    resultado_path = PASTA_RESULTADOS / f"recon_{dados.usuario}_{dados.algoritmo}_{dados.arquivo_g.replace('.csv', '')}.png"

    fig, ax = plt.subplots()
    ax.axis('off')
    ax.imshow(imagem, cmap='gray', vmin=0, vmax=1)

    plt.savefig(resultado_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return resultado_path


def salvar_log(dados, iteracoes, inicio, fim, resultado_path, job_id):
    log = {
        "usuario": dados.usuario,
        "algoritmo": dados.algoritmo,
        "arquivo_H": dados.arquivo_H,
        "arquivo_g": dados.arquivo_g,
        "iteracoes": iteracoes,
        "inicio": str(inicio),
        "fim": str(fim),
        "duracao": (fim - inicio).total_seconds(),
        "cpu": psutil.cpu_percent(),
        "memoria": psutil.virtual_memory().percent,
        "saida": str(resultado_path)
    }

    log_path = PASTA_RESULTADOS / f"log_{dados.usuario}_{dados.arquivo_g.replace('.csv', '')}.json"
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    jobs[job_id]["log"] = str(log_path)


# --------------------- Método principal ------------------------------------- #
def processamento(dados: RequisicaoReconstrucao, job_id: str):
    try:
        logger.info(f"[{dados.usuario}, {job_id}] Iniciando processamento")
        jobs[job_id]["status"] = "processando"

        aguardar_memoria(job_id)

        H, g_gain = carregar_dados(dados)

        inicio = datetime.now()
        f, iteracoes = reconstruir_imagem(H, g_gain, dados.algoritmo)
        fim = datetime.now()

        imagem = processar_imagem(f, dados.arquivo_H)
        resultado_path = salvar_imagem(imagem, dados)

        salvar_log(dados, iteracoes, inicio, fim, resultado_path, job_id)

        jobs[job_id]["status"] = "concluido"
        jobs[job_id]["resultado"] = str(resultado_path)

        logger.info(f"[{job_id}] Finalizado com sucesso. Resultado salvo em {resultado_path}")

    except Exception as e:
        jobs[job_id]["status"] = "erro"
        jobs[job_id]["erro"] = str(e)
        logger.error(f"[{job_id}] Erro no processamento: {e}")


# --------------------- Workers e filas ------------------------------------- #

def monitorar_memoria():
    return psutil.virtual_memory().percent < MEMORY_THRESHOLD


async def worker():
    """
    Worker assíncrono que consome a fila de requisições e delega o processamento
    pesado para threads, mantendo o event loop livre.

    Fluxo de execução:
    ------------------
    1. Aguarda um item na fila `requisicoes`, que deve ser uma tupla (dados, job_id).
    2. Obtém o event loop atual com `asyncio.get_running_loop()`.
    3. Executa a função bloqueante `processamento(dados, job_id)` em um executor
       (thread pool) para não bloquear o loop principal.
    4. Chama `requisicoes.task_done()` para sinalizar o término do processamento.

    Características:
    ----------------
    - Não aceita parâmetros e não retorna valor.
    - Roda indefinidamente enquanto a aplicação estiver ativa.
    - Garante que operações CPU‐bound não travem o servidor assíncrono.
    """
    while True:
        dados, job_id = await requisicoes.get()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, processamento, dados, job_id)

        requisicoes.task_done()


# noinspection PyAsyncCall,PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handler de ciclo de vida da aplicação FastAPI.

    Executa tarefas de inicialização (startup) antes de o servidor começar
    a aceitar requisições e tarefas de limpeza (shutdown) depois que o servidor
    for interrompido.

    """
    for _ in range(MAX_WORKERS):
        asyncio.create_task(worker())
    logger.info("Workers iniciados")

    # ponto em que o servidor entra em execução
    yield

    logger.info("Servidor finalizando...")


# ----------------------- Inicializar servidor -------------------------- #

# Inicializar app
app = FastAPI(lifespan=lifespan)


# ----------------------- Endpoints ------------------------------------- #

# Endpoint para submeter job
@app.post("/reconstruir")
async def reconstruir(dados: RequisicaoReconstrucao):
    """
    Endpoint para submeter uma nova tarefa de reconstrução.

    Parâmetros:
    -----------
    dados : RequisicaoReconstrucao
        Instância do modelo Pydantic contendo:
        - usuario (str): nome ou identificador do solicitante.
        - algoritmo (str): "cgne" ou "cgnr".
        - arquivo_H (str): nome do arquivo CSV da matriz H.
        - arquivo_g (str): nome do arquivo CSV dos valores g.
        - valores_g (list[float]): lista de valores de g já carregados em memória.

    Fluxo de execução:
    ------------------
    1. Gera um `job_id` único (UUID) para identificar a tarefa.
    2. Registra o job no dicionário `jobs` com status inicial `"na_fila"`.
    3. Enfileira a tupla `(dados, job_id)` na fila assíncrona `requisicoes`.
    4. Registra no log (`logger.info`) que o job foi adicionado à fila.
    5. Retorna imediatamente o JSON com:
       - `job_id`: identificador da tarefa.
       - `status`: `"na_fila"`, indicando que ainda não começou a processar.

    Retorno:
    --------
    dict
        {
            "job_id": str,
            "status": "na_fila"
        }

    Observações:
    ------------
    - A execução efetiva da tarefa ocorre em background pelos workers,
      garantindo que este endpoint não bloqueie o event loop.
    """
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "na_fila"}

    await requisicoes.put((dados, job_id))
    logger.info(f"[{job_id}] Adicionado à fila")

    return {"job_id": job_id, "status": "na_fila"}
