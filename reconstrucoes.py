import numpy as np
MAX_ITER = 20
TOL = 1e-4


def calcular_ganho_sinal(g):
    g = np.atleast_2d(g)
    if g.shape[0] == 1:
        g = g.T
    S, N = g.shape
    ganho = np.array([100 + (1/20) * l * np.sqrt(l) for l in range(1, S+1)], dtype=g.dtype).reshape(S, 1)
    return g * ganho


def calcular_fatores_regularizacao(H, g):
    HtH = H.T @ H
    Htg = H.T @ g
    c = np.linalg.norm(HtH, ord=2)
    lamb = np.max(np.abs(Htg)) * 0.01
    return lamb, c


def cgne(H, g, max_iter=MAX_ITER, tol=TOL):
    H = H.astype(np.float64)
    g = g.astype(np.float64)

    N = H.shape[1]
    lamb, c = calcular_fatores_regularizacao(H, g)

    f = np.zeros(N, dtype=np.float64)
    r = g.copy()
    p = H.T @ r
    rTr = np.dot(r, r)
    erros = np.empty(max_iter)

    for i in range(max_iter):
        Hp = H @ p
        HpTHp = np.dot(Hp, Hp)
        alpha = rTr / (HpTHp + lamb / c)

        f += alpha * p
        r_new = r - alpha * Hp
        rTr_new = np.dot(r_new, r_new)

        erro_dif = rTr_new - rTr
        erros[i] = np.sqrt(rTr_new)

        if abs(erro_dif) < tol:
            break

        beta = rTr_new / (rTr + 1e-12)
        p = H.T @ r_new + beta * p

        r = r_new
        rTr = rTr_new

    return f, erros[:i+1], i + 1


def cgnr(H, g, max_iter=MAX_ITER, tol=TOL):
    H = H.astype(np.float64)
    g = g.astype(np.float64)

    N = H.shape[1]
    lamb, c = calcular_fatores_regularizacao(H, g)

    f = np.zeros(N, dtype=np.float64)
    r = g.copy()
    z = H.T @ r
    p = z.copy()
    zTz = np.dot(z, z)
    rTr = np.dot(r, r)
    erros = np.empty(max_iter)

    for i in range(max_iter):
        w = H @ p
        wTw = np.dot(w, w)
        alpha = zTz / (wTw + lamb / c)

        f += alpha * p
        r_new = r - alpha * w

        rTr_new = np.dot(r_new, r_new)
        erro_dif = rTr_new - rTr
        erros[i] = np.sqrt(rTr_new)

        if abs(erro_dif) < tol:
            break

        z_new = H.T @ r_new
        zTz_new = np.dot(z_new, z_new)

        beta = zTz_new / (zTz + 1e-12)
        p = z_new + beta * p

        r = r_new
        z = z_new
        zTz = zTz_new
        rTr = rTr_new

    return f, erros[:i+1], i + 1
