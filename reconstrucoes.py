import numpy as np

# r: “resíduo” (diferença entre g e H@f)
# np.linalg.norm: calcula a norma euclidiana do vetor
# durante a convergência, esperamos que ‖r_novo‖ < ‖r_antigo‖, então esse valor tende a ser negativo (o resíduo diminui)
def erro_iterativo(r_novo, r_antigo):
    return np.linalg.norm(r_novo) - np.linalg.norm(r_antigo)

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
    f = np.zeros((H.shape[1],))
    r = g - H @ f
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
