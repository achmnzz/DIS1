import socket
import json
import random

host = 'localhost'
porta = 5000

mensagem = {
    "usuario": f"usuario_{random.randint(1, 100)}",
    "algoritmo": random.choice(["cgne", "cgnr"]),
    "arquivo_H": "H-2.csv",
    "arquivo_g": random.choice(["g-30x30-1.csv", "g-30x30-2.csv"]),
}

# Envio da requisição
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((host, porta))
    cliente.sendall(json.dumps(mensagem).encode('utf-8'))

print("Solicitação enviada ao servidor.")
