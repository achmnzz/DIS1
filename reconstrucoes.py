import numpy as np


def calcular_ganho_sinal(g):
    g = np.atleast_2d(g)
    if g.shape[0] == 1:
        g = g.T
    S, N = g.shape
    ganho = np.array([100 + (1/20) * l * np.sqrt(l) for l in range(1, S+1)]).reshape(S, 1)
    return g * ganho


def erro_iterativo(r_novo, r_antigo):
    return np.linalg.norm(r_novo) - np.linalg.norm(r_antigo)


def adicionar_regularizacao(H, g, fator=0.10):
    Ht = H.T
    lambda_reg = np.max(np.abs(Ht @ g)) * fator
    I = np.eye(H.shape[1])
    H_reg = np.vstack([H, np.sqrt(lambda_reg) * I])
    g_reg = np.concatenate([g, np.zeros(H.shape[1])])
    return H_reg, g_reg


def cgne(H, g, max_iter=100, tol=1e-10):
    H, g = adicionar_regularizacao(H, g)

    f = np.zeros((H.shape[1],))
    r = g.copy()
    p = H.T @ r
    erros = []

    for i in range(max_iter):
        Hp = H @ p
        alpha = np.dot(r, r) / np.dot(Hp, Hp)
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


def cgnr(H, g, max_iter=100, tol=1e-10):
    H, g = adicionar_regularizacao(H, g)

    f = np.zeros((H.shape[1],))
    r = g.copy()
    z = H.T @ r
    p = z.copy()
    erros = []

    for i in range(max_iter):
        w = H @ p
        alpha = np.dot(z, z) / np.dot(w, w)
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

# def cgne(H, g, max_iter=100, tol=1e-10):
#     f = np.zeros((H.shape[1],))
#     r = g - H @ f
#     p = H.T @ r
#     erros = []
#
#     for i in range(max_iter):
#         Hp = H @ p
#         alpha = np.dot(r, r) / np.dot(Hp, Hp)
#         f = f + alpha * p
#         r_new = r - alpha * Hp
#         erro = erro_iterativo(r_new, r)
#         erros.append(erro)
#         if np.linalg.norm(r_new) < tol:
#             break
#         beta = np.dot(r_new, r_new) / np.dot(r, r)
#         p = H.T @ r_new + beta * p
#         r = r_new
#
#     return f, erros, i + 1
#
#
# def cgnr(H, g, max_iter=100, tol=1e-10):
#     f = np.zeros((H.shape[1],))
#     r = g - H @ f
#     z = H.T @ r
#     p = z.copy()
#     erros = []
#
#     for i in range(max_iter):
#         w = H @ p
#         alpha = np.dot(z, z) / np.dot(w, w)
#         f = f + alpha * p
#         r_new = r - alpha * w
#         erro = erro_iterativo(r_new, r)
#         erros.append(erro)
#         if np.linalg.norm(r_new) < tol:
#             break
#         z_new = H.T @ r_new
#         beta = np.dot(z_new, z_new) / np.dot(z, z)
#         p = z_new + beta * p
#         r = r_new
#         z = z_new
#
#     return f, erros, i + 1
