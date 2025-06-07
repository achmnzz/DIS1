import numpy as np
MAX_ITER = None
TOL = 1e-6


def calcular_ganho_sinal(g):
    g = np.atleast_2d(g)
    if g.shape[0] == 1:
        g = g.T
    S, N = g.shape
    ganho = np.array([100 + (1/20) * l * np.sqrt(l) for l in range(1, S+1)]).reshape(S, 1)
    return g * ganho

# r: “resíduo” (diferença entre g e H@f)
# np.linalg.norm: calcula a norma euclidiana do vetor
# durante a convergência, esperamos que ‖r_novo‖ < ‖r_antigo‖, então esse valor tende a ser negativo (o resíduo diminui)
def erro_iterativo(r_novo, r_antigo):
    return np.linalg.norm(r_novo) - np.linalg.norm(r_antigo)

<<<<<<< HEAD
# H: matriz (tamanho m x n)
# g: vetor (tamanho m)
# max_iter: número máximo de iterações 
# tol: tolerância para o critério de parada
# H @ f: multiplicaçã0 da matriz H pelo vetor f
def cgne(H, g, max_iter=100, tol=1e-10):
    f = np.zeros((H.shape[1],)) # cria o vetor f com zeros, com comprimento igual ao número de colunas de H, começa a busca pela solução f a partir de zero
    r = g - H @ f
    p = H.T @ r # multiplicando a transposta de H (tamanho m x n) por r (tamanho m) obtém-se um vetor de tamanho n, que será a direção inicial
    erros = [] # lista que guarda, a cada iteração, o valor retornado por erro_iterativo (diferença das normas dos resíduos)

    for i in range(max_iter):
        Hp = H @ p # vetor de tamanho m, usado para computar o alpha
        alpha = np.dot(r, r) / np.dot(Hp, Hp)
=======

def calcular_fatores_regularizacao(H, g):
    HtH = H.T @ H
    Htg = H.T @ g
    c = np.linalg.norm(HtH, ord=2)
    lamb = np.max(np.abs(Htg)) * 0.10
    return lamb, c


def cgne(H, g, max_iter=MAX_ITER, tol=TOL):
    N = H.shape[1]
    if max_iter is None:
        max_iter = 2 * N  # número de colunas vezes 2 como padrão

    lamb, c = calcular_fatores_regularizacao(H, g)

    f = np.zeros(N)
    r = g.copy()
    p = H.T @ r
    erros = []

    for i in range(max_iter):
        Hp = H @ p
        alpha = np.dot(r, r) / (np.dot(Hp, Hp) + lamb / c)
>>>>>>> 49f1027b61d68eedf6612227c9385999170efab7
        f = f + alpha * p
        r_new = r - alpha * Hp
        erro = erro_iterativo(r_new, r)
        erros.append(erro)

        if np.linalg.norm(r_new) < tol:
            break

        beta = np.dot(r_new, r_new) / np.dot(r, r)
        p = H.T @ r_new + beta * p
        r = r_new

    return f, erros, i + 1


def cgnr(H, g, max_iter=MAX_ITER, tol=TOL):
    N = H.shape[1]
    if max_iter is None:
        max_iter = 2 * N

    lamb, c = calcular_fatores_regularizacao(H, g)

    f = np.zeros(N)
    r = g.copy()
    z = H.T @ r
    p = z.copy()
    erros = []

    for i in range(max_iter):
        w = H @ p
        alpha = np.dot(z, z) / (np.dot(w, w) + lamb / c)
        f = f + alpha * p
        r_new = r - alpha * w
        erro = erro_iterativo(r_new, r)
        erros.append(erro)

        if np.linalg.norm(r_new) < tol:
            break

        z_new = H.T @ r_new
        beta = np.dot(z_new, z_new) / np.dot(z, z)
        p = z_new + beta * p
        r = r_new
        z = z_new

    return f, erros, i + 1
