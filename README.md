## Descrição  
Este projeto é um servidor de reconstrução de imagens via FastAPI + asyncio, com uma fila de jobs e processamento em background. Também inclui um cliente assíncrono em Python que dispara várias requisições para teste de carga.

---

## Pré-requisitos  
- Python 3.9 ou superior  
- (Opcional) [conda](https://docs.conda.io/)  
- (Opcional) [Poetry](https://python-poetry.org/)  

---

## Instalação de dependências  

Você pode instalar todas as bibliotecas necessárias de três formas:

### 1. Usando `pip`  

```bash
source venv/bin/activate

windows .venv\Scripts\activate

pip install fastapi uvicorn numpy psutil matplotlib httpx
```
ou

```bash
conda install -c conda-forge fastapi uvicorn numpy psutil matplotlib httpx
```

```bash
poetry add fastapi uvicorn numpy psutil matplotlib httpx
```


```bash
projeto /

├── main.py               # Entrypoint (importa `app` de servidor_fastapi.py)
├── servidor_fastapi.py   # Lógica do servidor, fila e workers
├── reconstrucoes.py      # Implementação de cgne(), cgnr() e calcular_ganho_sinal()
├── cliente_async.py      # Cliente asyncio + httpx para testes de carga
├── Dados/                # CSVs de entrada (H-*.csv, g-*.csv, A-*.csv)
└── Resultados/           # PNGs e logs gerados pelo servidor
```

## Como rodar o servidor

### a) Modo desenvolvedor (com reload automático)
Na raiz do projeto, rode:

bash
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Abra no navegador:

 - Swagger UI: http://localhost:8000/docs

 - Redoc: http://localhost:8000/redoc

### b) Sem chamar uvicorn diretamente

Rodar o arquivo

```python
import uvicorn
from servidor_fastapi import app

if __name__ == "__main__":
    uvicorn.run("servidor_fastapi:app", host="0.0.0.0", port=8000, reload=True)

```

Execute:

``` bash
python main.py
```

# Request sample
```json
  http://localhost:8000/reconstruir \
  "Content-Type: application/json" \
  '{
        "usuario": "joao",
        "algoritmo": "cgne",
        "arquivo_H": "matriz_H.csv",
        "arquivo_g": "vetor_g.csv"
      }'

```