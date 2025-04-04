#include <stdlib.h>
#include <stdio.h>
#include <cblas.h>

#define TAM 10

void printa_matrix(int matrix[][TAM])
{
    for(int i = 0; i < TAM; i++)
    {
        for(int j = 0; j < TAM; j++)
        {
            printf("%5d", matrix[i][j]);
        }
        printf("\n");
    }
    printf("\n\n");
}

int main()
{
    int matrix_a[TAM][TAM], matrix_b[TAM][TAM];

    for(int i =  0; i < TAM; i++)
    {
        for(int j = 0; j < TAM; j++)
        {
            matrix_a[i][j] = rand() % 100;
            matrix_b[i][j] = rand() % 100;
        }
    }

    printa_matrix(matrix_a);
    printa_matrix(matrix_b);

    return (0);
}
