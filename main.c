#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "cblas.h"

#define num_linhas 10
#define num_colunas 10
#define dim_comum 10

void le_vetor (const char *nome_arquivo, float *vetor, int num_elementos)
{
    FILE *arquivo = fopen(nome_arquivo, "r");

    if (!arquivo)
        printf("Erro ao abrir o arquivo.");

    for (int i = 0; i < num_elementos; i++)
    {
        if (i < num_elementos - 1) 
            fscanf(arquivo, "%f;", &vetor[i]);  // lê até o próximo ponto e vírgula
        else 
            fscanf(arquivo, "%f", &vetor[i]);   // último elemento não precisa do ';'
    }

    fclose(arquivo);
}

void le_matriz (const char *nome_arquivo, float *matriz, int linhas, int colunas) 
{
    FILE *arquivo = fopen(nome_arquivo, "r");

    if (!arquivo)
        printf("Erro ao abrir o arquivo.");

    for (int i = 0; i < linhas; i++)
    {
        for (int j = 0; j < colunas; j++)
        {
            if (j < colunas-1) 
                fscanf(arquivo, "%f;", &matriz[i*colunas + j]);
            else           
                fscanf(arquivo, "%f",  &matriz[i*colunas + j]);
        }
    }

    fclose(arquivo);
}

int compara_vetores(float *vetor_1, float *vetor_2, int num_elementos, double tolerancia) {
    for (int i = 0; i < num_elementos; i++)
        if (fabs(vetor_1[i] - vetor_2[i]) > tolerancia) 
            return 0;

    return 1;
}

int compara_matrizes(float *matriz_1, float *matriz_2, int linhas, int colunas, double tolerancia) {
    for (int i = 0; i < linhas*colunas; i++)
        if (fabs(matriz_1[i] - matriz_2[i]) > tolerancia) 
            return 0;

    return 1;
}

int main()
{
    float *vetor_a = malloc(dim_comum * sizeof(float));                      
    float *matriz_M = malloc(dim_comum * num_colunas * sizeof(float));       
    float *matriz_N = malloc(num_linhas * dim_comum * sizeof(float));         
    float *vetor_resultado_aM = malloc(dim_comum * sizeof(float));      
    float *matriz_resultado_MN = malloc(num_linhas * num_colunas * sizeof(float));    
    float *vetor_gabarito_aM = malloc(num_colunas * sizeof(float));                  
    float *matriz_gabarito_MN = malloc(num_linhas * num_colunas * sizeof(float));    

    le_vetor("dados/a.csv",  vetor_a, num_colunas);
    le_matriz("dados/M.csv", matriz_M, dim_comum, num_colunas);
    le_matriz("dados/N.csv", matriz_N, num_linhas, dim_comum);
    le_vetor("dados/aM.csv", vetor_gabarito_aM, num_colunas);
    le_matriz("dados/MN.csv", matriz_gabarito_MN, num_linhas, num_colunas);

    // a * M 
    cblas_sgemv(CblasRowMajor, CblasTrans, num_linhas, 
        dim_comum, 1.0f, matriz_M, 
        dim_comum, vetor_a, 1, 
        0.0f, vetor_resultado_aM, 1);

    // M * N 
    cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans,
        num_linhas, num_colunas, dim_comum,
        1.0f, matriz_M, dim_comum,
        matriz_N, num_colunas, 0.0f, 
        matriz_resultado_MN, num_colunas);

    // impressão dos resultados obtidos e dos resultados esperados 
    printf("\nResultado obtido vs esperado para a*M:\n");

    printf("    Obtido        Esperado\n");
    for (int i = 0; i < num_colunas; i++) 
        printf("%10.2f    %10.2f\n", vetor_resultado_aM[i], vetor_gabarito_aM[i]);

    printf("\nResultado obtido vs esperado para M*N:\n");

    printf("     Obtido                                                                                                           Esperado \n");
    for (int i = 0; i < dim_comum; i++) 
    {
        for (int j = 0; j < num_colunas; j++) 
            printf("%10.0f ", matriz_resultado_MN[i*dim_comum + j]);
    
        printf("   ");

        for (int j = 0; j < num_colunas; j++) 
            printf("%10.0f ", matriz_gabarito_MN[i*num_colunas + j]);
        
        printf("\n");
    }

    // comparação dos resultados com tolerância de 0.01
    printf("\nComparando resultados com valores esperados (tolerancia de 0.01):\n");
    
    if (compara_vetores(vetor_resultado_aM, vetor_gabarito_aM, num_colunas, 0.01))
        printf("a*M: OK (dentro da tolerancia)\n");
    else
        printf("a*M: ERRO (fora da tolerancia)\n");

    if (compara_matrizes(matriz_resultado_MN, matriz_gabarito_MN, dim_comum, num_colunas, 0.01))
        printf("M*N: OK (dentro da tolerancia)\n");
    else
        printf("M*N: ERRO (fora da tolerancia)\n");

    printf("\n\n\n");

    free(vetor_a); 
    free(matriz_M); 
    free(matriz_N); 
    free(vetor_resultado_aM); 
    free(matriz_resultado_MN);
    free(vetor_gabarito_aM);
    free(matriz_gabarito_MN);

    return 0; 
} 

/*
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

/*
int main()
{
    float A[M*K], B[K*N], result[M*N] = {}; 
    float vetor[K], vetor_2[M], vetor_result[M] = {}, vetor_result2[K] = {};

    inicializa_(A, B, vetor, vetor_2);
   
    printf("A:\n");
    printa_(M, K, A);
    printf("B:\n");
    printa_(K, N, B);
    printf("X1: \n");
    printa_(1, K, vetor);
    printf("X2: \n");
    printa_(1, M, vetor_2);
  
     // MULTIPLICAÇÃO DE MATRIZES, C = alpha*A*B + beta*C
     // Parâmetros:
     // Layout: a matriz é um vetor onde as linhas (CblasRowMajor) ou as colunas
     // (CblasColumnMajor) são armazenadas em sequencia na memória
     // TransA, TransB: Se a matrix é transposta (CblasTrans) ou não (CblasNoTrans)
     // M, N e K: matriz A (M x K) * matriz B (K x N). São as dimensões das matrizes 
     // alpha: multiplica o resultado por um escalar alpha, para ignorar deixar com valor 1
     // A, B, C: ponteiro para as matrizes
     // IdA, IdB, IdC:  tamanho de cada segmento baseado no Layout, na CblasRowMajor é o
     // número de colunas da matriz e no CblasColumnMajor o número de linhas
     // beta: multiplica C antes de se agregar ao resultado da multiplicação das matrizes, 
     // para ignorar deixar com valor zero
     

    // result = A*B
    cblas_sgemm(CblasRowMajor, CblasNoTrans, CblasNoTrans, M, N, K, 1.0f, A, K, B, N, 0.0f, result, N);
    printf("Resultado de A*B: \n");
    printa_(M, N, result);


     // MULTIPLICAÇÃO DE MATRIZ POR VETOR, Y = alpha*A*X + beta*Y
     // Parâmetros: (vários são idênticos ao anterior, não vou repetir)
     // X: ponteiro para o vetor que está multiplicando a matriz
     // incX, incY: incremento entre os elementos do vetor (para considerar todos use 1)
     // Y: ponteiro para o vetor resultado     
    
    // vetor_result = A*vetor
    cblas_sgemv(CblasRowMajor, CblasNoTrans, M, K, 1.0f, A, K, vetor, 1, 0.0f, vetor_result, 1);
    printf("Resultado de A*vetor: \n");
    printa_(M, 1, vetor_result);

     // MULTIPLICAÇÃO DE VETOR POR MATRIZ, Y = alpha*At*X + beta*Y
     // Mesma coisa do anterior, mas a Matriz é transposta
     
    
    // vetor_result = vetor*A
    cblas_sgemv(CblasRowMajor, CblasTrans, M, K, 1.0f, A, K, vetor_2, 1, 0.0f, vetor_result2, 1);
    printf("Resultado de vetor*A: \n");
    printa_(K, 1, vetor_result2);

    return (0);
}
*/