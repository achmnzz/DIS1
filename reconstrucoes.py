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
