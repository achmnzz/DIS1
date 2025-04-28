#include <stdlib.h>
#include <stdio.h>
#include "cblas.h"

#define M 2
#define N 2
#define de_um_ate_ 3

void inicializa_(float matrix_a[M*N], float matrix_b[M*N], float vetor_[M])
{
    inicializa_valores(M, N, matrix_a);
    inicializa_valores(M, N, matrix_b);
    inicializa_valores(1, M, vetor_);
}

void inicializa_valores(int linhas, int colunas, float matrix[linhas*colunas])
{
     for(int i =  0; i < linhas; i++)
     {
        for(int j = 0; j < colunas; j++)
         {
            matrix[i*colunas+j] = (float) ((rand() % de_um_ate_)+ 1);
         }
     }
}

void printa_(int linhas, int colunas, float matrix[linhas*colunas])
{
    for(int i = 0; i < linhas; i++)
    {
        for(int j = 0; j < colunas; j++)
        {
            printf("%10.1f", matrix[i*linhas+j]);
        }
        printf("\n");
    }
    printf("\n\n");
}

int main()
{
    float A[M*N], B[M*N], result[M*N] = {0}, vetor[M], vetor_result[M] = {0};

    inicializa_(A, B, vetor);
   
    printf("A: \n");
    printa_(M, N, A);
    printf("B: \n");
    printa_(M, N, B);
    printf("Vetor: \n");
    printa_(1, M, vetor);

    //result = A*B
    /**************************************
     * Parâmetros:
     * Layout: definido pela biblioteca (vê o vetor como um matriz?)
     * TransA: Se a matrix é transposta (CblasTrans) ou não (CblasNoTrans)
     * M, N e K: matriz A (M x K) * matriz B (K x N) 
     * alpha: multiplica o resultado por um escalar alpha, para ignorar multiplicar por 1
     * 
     **************************************
    */
    cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, M, N, M, 1.0f, A, M, B, N, 0.0f, result, N);
    printf("Resultado de A*B: \n");
    printa_(M, N, result);

    //vetor_result = A*vetor
    cblas_sgemv(CblasRowMajor, CblasNoTrans, M, N, 1.0f, A, N, vetor, 1, 0.0f, vetor_result, 1);
    printf("Resultado de A*vetor: \n");
    printa_(1, M, vetor_result);

    //vetor_result = vetor*A
    cblas_sgemv(CblasRowMajor, CblasTrans, M, N, 1.0f, A, N, vetor, 1, 0.0f, vetor_result, 1);
    printf("Resultado de vetor*A: \n");
    printa_(1, M, vetor_result);

    return (0);
}
