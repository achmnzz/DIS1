import asyncio
import httpx
import json
import random
import numpy as np
import psutil
from pathlib import Path
from datetime import datetime

# Configurações
PASTA_DADOS = Path(__file__).parent.resolve() / "Dados"
PASTA_RESULTADOS = Path(__file__).parent.resolve() / "Resultados"
PASTA_RESULTADOS.mkdir(exist_ok=True)

host = 'localhost'
porta = 8000
url = f"http://{host}:{porta}/reconstruir"

# Parâmetros do teste
NUM_CLIENTES = 3
REQUISICOES_POR_CLIENTE = 10
INTERVALO_MIN = 1.0
INTERVALO_MAX = 3.0

# Gera lista de clientes com números aleatórios de 1 a 100
ids = random.sample(range(1, 101), NUM_CLIENTES)
CLIENTES = [f"usuario_{i}" for i in ids]

# Monitoramento
memorias = []
cpus = []
inicio = datetime.now()


def gerar_requisicao(usuario: str):
    """
    Gera o payload JSON usando um usuário fixo.
    """
    algoritmo = random.choice(["cgne", "cgnr"])
    arquivo_H = random.choice(["H-1.csv", "H-2.csv"])

    if arquivo_H == "H-1.csv":
        arquivo_g = random.choice(["g-60x60-1.csv", "g-60x60-2.csv", "A-60x60-1.csv"])
    else:
        arquivo_g = random.choice(["g-30x30-1.csv", "g-30x30-2.csv", "A-30x30-1.csv"])

    g_path = PASTA_DADOS / arquivo_g
    g_valores = np.loadtxt(g_path, delimiter=',').tolist()

    return {
        "usuario": usuario,
        "algoritmo": algoritmo,
        "arquivo_H": arquivo_H,
        "arquivo_g": arquivo_g,
        "valores_g": g_valores
    }, arquivo_g


async def enviar_requisicao(usuario: str, req_id: int, client: httpx.AsyncClient):
    """
    Envia uma requisição para o servidor e registra tempo de espera.
    """
    mensagem, arquivo_g = gerar_requisicao(usuario)
    try:
        resposta = await client.post(url, json=mensagem)
        if resposta.status_code == 200:
            print(f"[{usuario}] Req {req_id} OK ({arquivo_g}: {resposta.text})")
        else:
            print(f"[{usuario}] Req {req_id} ERRO {resposta.status_code}: {resposta.text}")
    except Exception as e:
        print(f"[{usuario}] Req {req_id} FALHOU: {e}")

    cpus.append(psutil.cpu_percent(interval=0.05))
    memorias.append(psutil.virtual_memory().percent)

    await asyncio.sleep(random.uniform(INTERVALO_MIN, INTERVALO_MAX))


async def cliente_simulado(usuario: str, client: httpx.AsyncClient):
    """
    Cada cliente envia várias requisições sequencialmente, aguardando entre elas.
    """
    for i in range(1, REQUISICOES_POR_CLIENTE + 1):
        await enviar_requisicao(usuario, i, client)


async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [asyncio.create_task(cliente_simulado(usuario, client)) for usuario in CLIENTES]
        await asyncio.gather(*tasks)

# Executa o loop e depois gera relatório
asyncio.run(main())

# Relatório de desempenho
fim = datetime.now()
relatorio = {
    "clientes": len(CLIENTES),
    "ids_clientes": CLIENTES,
    "total_requisicoes": len(CLIENTES) * REQUISICOES_POR_CLIENTE,
    "inicio": str(inicio),
    "fim": str(fim),
    "duracao_segundos": (fim - inicio).total_seconds(),
    "cpu_medio": round(sum(cpus) / len(cpus), 2) if cpus else 0,
    "memoria_media": round(sum(memorias) / len(memorias), 2) if memorias else 0,
    "uso_cpu": cpus,
    "uso_memoria": memorias
}

relatorio_path = PASTA_RESULTADOS / "relatorio_stress_teste_async.json"
with open(relatorio_path, 'w') as f:
    json.dump(relatorio, f, indent=2)

print(f"[RELATÓRIO] Salvo em: {relatorio_path}")
