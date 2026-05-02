import numpy as np

def calcular_pesos_ahp(matriz_comparacao):
    """
    Realiza o cálculo completo do AHP (Pesos e Consistência) para matrizes de qualquer tamanho.
    """
    n = matriz_comparacao.shape[0]
    
    # 1. Normalização e Pesos
    soma_colunas = matriz_comparacao.sum(axis=0)
    matriz_normalizada = matriz_comparacao / soma_colunas
    pesos = matriz_normalizada.mean(axis=1)
    
    # 2. Cálculo da Consistência
    vetor_ponderado = np.dot(matriz_comparacao, pesos)
    lambda_max = (vetor_ponderado / pesos).mean()
    
    # Índice de Consistência (CI)
    ci = (lambda_max - n) / (n - 1)
    
    # 3. Índice Aleatório (RI) Expandido
    # Tabela clássica de Saaty/Oak Ridge até 15 variáveis
    ri_dict = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 
               6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
               11: 1.51, 12: 1.53, 13: 1.56, 14: 1.57, 15: 1.59}
    
    # Se passar de 15 variáveis, usa a fórmula de aproximação de Alonso e Lamata
    if n in ri_dict:
        ri = ri_dict[n]
    else:
        ri = 1.98 * (n - 2) / n
    
    # Razão de Consistência (CR)
    cr = ci / ri if ri > 0 else 0
    consistente = cr <= 0.10
    
    return pesos, cr, consistente

def normalizar_dados_jogadores(df, criterios, tipos):
    """
    Normaliza os dados dos jogadores para uma escala de 0 a 1.
    df: Tabela de jogadores
    criterios: Lista com o nome das colunas analisadas
    tipos: Lista indicando se o critério é 'beneficio' (quanto maior, melhor - ex: Gols) 
           ou 'custo' (quanto menor, melhor - ex: Salário)
    """
    df_normalizado = df.copy()
    
    for criterio, tipo in zip(criterios, tipos):
        valor_min = df_normalizado[criterio].min()
        valor_max = df_normalizado[criterio].max()
        
        if tipo == 'beneficio':
            # Fórmula: (Valor - Min) / (Max - Min)
            df_normalizado[criterio] = (df_normalizado[criterio] - valor_min) / (valor_max - valor_min)
        elif tipo == 'custo':
            # Fórmula: (Max - Valor) / (Max - Min)
            df_normalizado[criterio] = (valor_max - df_normalizado[criterio]) / (valor_max - valor_min)
            
    return df_normalizado