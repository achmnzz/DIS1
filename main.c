#include <stdlib.h>
#include <stdio.h>
#include "cblas.h"

#define M 3
#define K 4
#define N 2
#define de_um_ate_ 5

void inicializa_valores(int linhas, int colunas, float matrix[])
{
     for(int i =  0; i < linhas; i++)
     {
        for(int j = 0; j < colunas; j++)
         {
            matrix[i*colunas+j] = (float) ((rand() % de_um_ate_)+ 1);
         }
     }
}

void inicializa_(float matrix_a[], float matrix_b[], float vector_[], float vector_2[])
{
    inicializa_valores(M, K, matrix_a);
    inicializa_valores(K, N, matrix_b);
    inicializa_valores(K, 1, vector_);
    inicializa_valores(M, 1, vector_2);
}

void printa_(int linhas, int colunas, float matrix[])
{
    for(int i = 0; i < linhas; i++)
    {
        for(int j = 0; j < colunas; j++)
        {
            printf("%10.1f", matrix[i*colunas+j]);
        }
        printf("\n");
    }
    printf("\n\n");
}

int main()
{
    float A[M*K], B[K*N], result[M*N] = {}, vetor[K], vetor_2[M], vetor_result[M] = {}, vetor_result2[K] = {};

    inicializa_(A, B, vetor, vetor_2);
   
    printf("A:\n");
    printa_(M, K, A);
    printf("B:\n");
    printa_(K, N, B);
    printf("X1: \n");
    printa_(K, 1, vetor);
    printf("X2: \n");
    printa_(M, 1, vetor_2);

    /*PRINTS DE TESTE
    printf("C:\n");
    printa_(M, N, result); 
    printf("Y1: \n");
    printa_(M, 1, vetor_result);
    printf("Y2: \n");
    printa_(K, 1, vetor_result2);*/

    
    /**************************************
     * MULTIPLICAÇÃO DE MATRIZES, C = alpha*A*B + beta*C
     * Parâmetros:
     * Layout: a matriz é um vetor onde as linhas (CblasRowMajor) ou as colunas
     * (CblasColumnMajor) são armazenadas em sequencia na memória
     * TransA, TransB: Se a matrix é transposta (CblasTrans) ou não (CblasNoTrans)
     * M, N e K: matriz A (M x K) * matriz B (K x N). São as dimensões das matrizes 
     * alpha: multiplica o resultado por um escalar alpha, para ignorar deixar com valor 1
     * A, B, C: ponteiro para as matrizes
     * IdA, IdB, IdC:  tamanho de cada segmento baseado no Layout, na CblasRowMajor é o
     * número de colunas da matriz e no CblasColumnMajor o número de linhas
     * beta: multiplica C antes de se agregar ao resultado da multiplicação das matrizes, 
     * para ignorar deixar com valor zero
     **************************************
    */
   //result = A*B
    cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, M, N, K, 1.0f, A, K, B, N, 0.0f, result, N);
    printf("Resultado de A*B: \n");
    printa_(M, N, result);


    /**************************************
     * MULTIPLICAÇÃO DE MATRIZ POR VETOR, Y = alpha*A*X + beta*Y
     * Parâmetros: (vários são idênticos ao anterior, não vou repetir)
     * X: ponteiro para o vetor que está multiplicando a matriz
     * incX, incY: incremento entre os elementos do vetor (para considerar todos use 1)
     * Y: ponteiro para o vetor resultado     
     **************************************
    */
    //vetor_result = A*vetor
    cblas_sgemv(CblasRowMajor, CblasNoTrans, M, K, 1.0f, A, K, vetor, 1, 0.0f, vetor_result, 1);
    printf("Resultado de A*vetor: \n");
    printa_(M, 1, vetor_result);

     /**************************************
     * MULTIPLICAÇÃO DE VETOR POR MATRIZ, Y = alpha*At*X + beta*Y
     * Mesma coisa do anterior, mas a Matriz é transposta
     **************************************
    */
    //vetor_result = vetor*A
    cblas_sgemv(CblasRowMajor, CblasTrans, M, K, 1.0f, A, K, vetor_2, 1, 0.0f, vetor_result2, 1);
    printf("Resultado de vetor*A: \n");
    printa_(K, 1, vetor_result2);

    return (0);
}
