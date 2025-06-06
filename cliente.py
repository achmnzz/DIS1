import socket
import json
import random
import numpy as np

host = 'localhost'
porta = 5000

usuario = f"usuario_{random.randint(1, 100)}"
algoritmo = random.choice(["cgne", "cgnr"])
arquivo_H = "H-2.csv"
# arquivo_H = random.choice(["H-1.csv", "H-2.csv"])
if arquivo_H == "H-1.csv":
    arquivo_g = random.choice(["g-60x60-1.csv", "g-60x60-2.csv", "A-60x60-1.csv"])
else:
    arquivo_g = random.choice(["g-30x30-1.csv", "g-30x30-2.csv", "A-30x30-1.csv"])

g_path = f"./Dados/{arquivo_g}"
g_valores = np.loadtxt(g_path, delimiter=',').tolist()

mensagem = {
    "usuario": usuario,
    "algoritmo": algoritmo,
    "arquivo_H": arquivo_H,
    "arquivo_g": arquivo_g,
    "valores_g": g_valores
}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    cliente.connect((host, porta))
    cliente.sendall(json.dumps(mensagem).encode('utf-8'))

print(f"Solicitação enviada ao servidor com g embutido ({arquivo_g}).")
