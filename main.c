#include <stdlib.h>
#include <stdio.h>
#include "cblas.h"

#define M 2
#define N 2

void printa_matrix(float matrix[M*N])
{
    for(int i = 0; i < M; i++)
    {
        for(int j = 0; j < N; j++)
        {
            printf("%10.1f", matrix[i*M+j]);
        }
        printf("\n");
    }
    printf("\n\n");
}

void transposta(int linhas, int colunas, float matrix[linhas*colunas], float transp[colunas*linhas])
{
    for(int j = 0; j < colunas; j++)
    {
        for(int i =  0; i < linhas; i++)
        {
            transp[i*linhas+j] = matrix[j*linhas+i];
        }
    }
}


int main()
{
    float A[M*N], B[M*N], A_t[N*M], B_t[N*M], result[M*N];

    for(int i =  0; i < M; i++)
    {
        for(int j = 0; j < N; j++)
        {
            A[i*M+j] = (float) (rand() % 3 + 1);
            B[i*M+j] = (float) (rand() % 3 + 1);
        }
    }

    printf("A: \n");
    printa_matrix(A);
    printf("B: \n");
    printa_matrix(B);

    cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, M, N, M, 1.0f, A, M, B, N, 0.0f, result, N);
    printf("Result: \n");
    printa_matrix(result);

    return (0);
}
