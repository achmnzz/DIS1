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
        if (fabs(vetor_1[i] - vetor_2[i]) > tolerancia) // fabs retorna o valor absoluto
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
    printf("Resultado obtido vs esperado para a*M:");
    printf("\nObtido:\n");
    for (int i = 0; i < num_colunas; i++) 
        printf("%10.2f  ", vetor_resultado_aM[i]);
    printf("\nEsperado:\n");   
        for (int i = 0; i < num_colunas; i++) 
        printf("%10.2f  ", vetor_gabarito_aM[i]);
    printf("\n\n");

    printf("Resultado obtido vs esperado para M*N:");
    printf("\nObtido:\n");
    for (int i = 0; i < num_linhas; i++) 
    {
        for (int j = 0; j < num_colunas; j++) 
            printf("%10.0f", matriz_resultado_MN[i*dim_comum + j]);
        printf("\n");
    }
    printf("Esperado:\n");
    for (int i = 0; i < num_linhas; i++) 
    {
        for (int j = 0; j < num_colunas; j++) 
            printf("%10.0f", matriz_gabarito_MN[i*num_colunas + j]);
        printf("\n");
    }

    // comparação dos resultados com tolerância de 0.01
    printf("\n\nComparando resultados com valores esperados (tolerancia de 0.01):\n");
    
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