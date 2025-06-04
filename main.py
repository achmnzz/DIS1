import numpy as np
import os


def carregar_csv(caminho):
    return np.loadtxt(caminho, delimiter=',')


def calcular_ganho_sinal(g):
    g = np.atleast_2d(g)
    if g.shape[0] == 1:
        g = g.T
    S, N = g.shape
    ganho = np.array([100 + (1/20) * (l+1)**1.5 for l in range(S)]).reshape(S, 1)
    return g * ganho


def fator_de_reducao(H):
    return np.linalg.norm(H.T @ H, ord=2)


def coeficiente_regularizacao(H, g):
    return np.max(np.abs(H.T @ g)) * 0.10


def erro_iterativo(r_novo, r_antigo):
    return np.linalg.norm(r_novo) - np.linalg.norm(r_antigo)


def cgne(H, g, max_iter=100, tol=1e-6):
    f = np.zeros((H.shape[1],))
    r = g - H @ f
    p = H.T @ r
    erros = []

    for i in range(max_iter):
        Hp = H @ p
        alpha = r @ r / (Hp @ Hp)
        f = f + alpha * p
        r_new = r - alpha * Hp
        erro = erro_iterativo(r_new, r)
        erros.append(erro)
        if np.linalg.norm(r_new) < tol:
            break
        beta = r_new @ r_new / (r @ r)
        p = H.T @ r_new + beta * p
        r = r_new

    return f, erros


def cgnr(H, g, max_iter=100, tol=1e-6):
    f = np.zeros((H.shape[1],))
    r = g - H @ f
    z = H.T @ r
    p = z.copy()
    erros = []

    for i in range(max_iter):
        w = H @ p
        alpha = (z @ z) / (w @ w)
        f = f + alpha * p
        r_new = r - alpha * w
        erro = erro_iterativo(r_new, r)
        erros.append(erro)
        if np.linalg.norm(r_new) < tol:
            break
        z_new = H.T @ r_new
        beta = (z_new @ z_new) / (z @ z)
        p = z_new + beta * p
        r = r_new
        z = z_new

    return f, erros


def executar_modelo(pasta, nome_H, nome_A, nomes_g):
    print(f"\n--- Executando modelo com H: {nome_H} ---")
    H = carregar_csv(os.path.join(pasta, nome_H))
    A = carregar_csv(os.path.join(pasta, nome_A))

    for nome_g in nomes_g:
        G = carregar_csv(os.path.join(pasta, nome_g))
        G_gain = calcular_ganho_sinal(G)
        g_vetor = G_gain.flatten()

        c = fator_de_reducao(H)
        lambd = coeficiente_regularizacao(H, g_vetor)

        print(f"\nArquivo de entrada: {nome_g}")
        print(f"Fator de redução (c): {c:.4f}")
        print(f"Coeficiente de regularização (λ): {lambd:.4f}")

        f_cgne, erros_cgne = cgne(H, g_vetor)
        f_cgnr, erros_cgnr = cgnr(H, g_vetor)

        print(f"CGNE: Erro final: {erros_cgne[-1]:.4e}, Iterações: {len(erros_cgne)}")
        print(f"CGNR: Erro final: {erros_cgnr[-1]:.4e}, Iterações: {len(erros_cgnr)}")

        # Salvar resultado opcionalmente
        np.savetxt(os.path.join(pasta, f"resultado_CGNE_{nome_g}"), f_cgne, delimiter=',')
        np.savetxt(os.path.join(pasta, f"resultado_CGNR_{nome_g}"), f_cgnr, delimiter=',')


pasta_dados = "./Dados"
executar_modelo(pasta_dados, "H-1.csv", "A-60x60-1.csv", ["g-60x60-1.csv", "g-60x60-2.csv"])
executar_modelo(pasta_dados, "H-2.csv", "A-30x30-1.csv", ["g-30x30-1.csv", "g-30x30-2.csv"])
