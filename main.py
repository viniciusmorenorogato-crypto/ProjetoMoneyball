import pandas as pd
import warnings
import numpy as np
from Funções import valor
from Funções import data
from Funções import ahp

warnings.filterwarnings("ignore")

def gerar_ranking(df_bruto):

    # ==========================================
    # 1. CARREGAMENTO DA PLANILHA
    # ==========================================

    # Como a planilha está na mesma pasta que este script, usamos apenas o nome.
    # Note que adicionei a engine 'openpyxl' pois seu arquivo é um .xlsm
    try:
        try:
            # Recortando da coluna A (posição 0) até a CK (posição 89, limite exclusivo)
            df_posicao_limpo = df_bruto.iloc[:, 0:89]

            # Limpando linhas vazias na primeira coluna
            df_posicao_limpo = df_posicao_limpo.dropna(subset=[df_posicao_limpo.columns[0]])

            print(f"\nTabela limpa! Ficamos com {df_posicao_limpo.shape[0]} jogadores e {df_posicao_limpo.shape[1]} colunas.")
            print(df_posicao_limpo.head())
                
        except FileNotFoundError:
            print("Verifique se a planilha está salva EXATAMENTE na mesma pasta que este script Python.")

        #print("\n--- Nomes exatos das colunas na tabela ---")
        #print(df_posicao_limpo.columns.tolist())

        # ==========================================
        # 2. TRATAMENTO DO VALOR DE MERCADO
        # ==========================================

        nome_coluna_valor = 'Valor estimado'

        # Aplica a limpeza chamando a função do arquivo minhas_funcoes.py
        df_posicao_limpo['Valor_Numerico'] = df_posicao_limpo[nome_coluna_valor].apply(valor.limpar_valor_mercado)

        # Encontra o valor máximo verdadeiro da coluna (ignorando os -1 temporários)
        valor_maximo_real = df_posicao_limpo[df_posicao_limpo['Valor_Numerico'] > 0]['Valor_Numerico'].max()

        # Substitui todos os inegociáveis (-1) pelo (valor_maximo_real * 2)
        novo_valor_inegociaveis = valor_maximo_real * 2
        df_posicao_limpo.loc[df_posicao_limpo['Valor_Numerico'] == -1, 'Valor_Numerico'] = novo_valor_inegociaveis

        # ==========================================
        # 3. TRATAMENTO DO SALÁRIO
        # ==========================================

        # Substitua 'Salário' pelo nome exato do cabeçalho na sua folha de cálculo
        nome_coluna_salario = 'Salário' 

        # Aplica a nova função de limpeza
        df_posicao_limpo['Salario_Numerico'] = df_posicao_limpo[nome_coluna_salario].apply(valor.limpar_salario)

        # ==========================================
        # 4. TRATAMENTO DO FIM DE CONTRATO
        # ==========================================

        # Substitua pelo nome exato do cabeçalho da sua planilha (ex: 'Expira', 'Fim do Contrato')
        nome_coluna_contrato = 'Data final de contrato'
        df_posicao_limpo['Contrato_Numerico'] = df_posicao_limpo[nome_coluna_contrato].apply(data.limpar_data_contrato)

        # ==========================================
        # 5. EXPORTAR PARA UMA NOVA PLANILHA
        # ==========================================

        colunas_para_ver = ['Valor_Numerico', 
                            'Idade', 
                            'Salario_Numerico', 
                            'Altura', 
                            'Contrato_Numerico',
                            'Jogos completos',
                            'Expected Goals Prevented xGP',
                            'Falhas/90',
                            '% Acerto do goleiro',
                            'Defesas totais / Jogo',
                            'Nota média'
                            ]

        nome_arquivo_final = "posicao_Moneyball_Limpos.xlsx"
        df_posicao_exportacao = df_posicao_limpo[colunas_para_ver]
        print(f"\nExportando dados para '{nome_arquivo_final}'...")
        df_posicao_exportacao.to_excel(nome_arquivo_final, index=False, engine='openpyxl')

        # ==========================================
        # 6. ONDE O FILHO CHORA E O PAI NÃO VÊ: AHP PARA DEFINIR OS PESOS DOS CRITÉRIOS
        # ==========================================

        nivel_1 = ['Expected Goals Prevented xGP', 'Altura', 'Jogos completos', 'Defesas totais / Jogo', 'Nota média']
        nivel_2 = [ 
            'Idade', 
            'Falhas/90', 
            '% Acerto do goleiro', 
        ]
        nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]

        def obter_nivel(criterio):
            if criterio in nivel_1: return 1
            elif criterio in nivel_2: return 2
            else: return 3

        criterios = nivel_1 + nivel_2 + nivel_3
        n = len(criterios)

        matriz_saaty = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                t_i = obter_nivel(criterios[i])
                t_j = obter_nivel(criterios[j])
                
                # Comparações
                if t_i == 1 and t_j == 2: val = 2.0       # T1 > T2
                elif t_i == 1 and t_j == 3: val = 9.0     # T1 >> T3
                elif t_i == 2 and t_j == 3: val = 5.0     # T2 > T3
                elif t_i == 2 and t_j == 1: val = 1/2     # T2 < T1
                elif t_i == 3 and t_j == 1: val = 1/9     # T3 << T1
                elif t_i == 3 and t_j == 2: val = 1/5     # T3 < T2
                else: val = 1.0                           # Empate (Mesmo nível)
                
                matriz_saaty[i, j] = val

        print("\nMatriz de Comparação de Pares (Saaty):")
        print(pd.DataFrame(matriz_saaty, index=criterios, columns=criterios))   

        pesos, cr, consistente = ahp.calcular_pesos_ahp(matriz_saaty)

        #print("\n--- RESULTADOS DO AHP ---")
        #print(f"Pesos dos Critérios: {pesos}")
        #print(f"Taxa de Consistência (CR): {cr:.4f}")
        #print(f"A matriz é consistente? {'Sim' if consistente else 'Não (Revise as notas da matriz)'}")

        # ==========================================
        # 7. AQUI O FILHO TERMINA DE CHORAR: REALIZAÇÃO DO RANKING FINAL COM BASE NOS PESOS DO AHP
        # ==========================================

        criterios_de_custo = [
            'Valor_Numerico', 
            'Salario_Numerico', 
            'Falhas/90',
            'Idade',
            'Contrato_Numerico'
        ]

        df_ranking = df_posicao_limpo[colunas_para_ver].copy()
        df_ranking['Nota_Moneyball'] = 0.0 # Inicializamos a nota com zero

        for criterio, peso in zip(criterios, pesos):
            
            # Prevenção: garante que o critério realmente existe na tabela de posicao
            if criterio in df_ranking.columns:
                val_max = df_ranking[criterio].max()
                val_min = df_ranking[criterio].min()
                
                # Evita divisão por zero caso todos os jogadores tenham o mesmo número
                if val_max == val_min:
                    df_ranking[f'{criterio}_Norm'] = 0.0
                else:
                    if criterio in criterios_de_custo:
                        # Matemática para Custo (Invertida: o menor ganha nota 1)
                        df_ranking[f'{criterio}_Norm'] = (val_max - df_ranking[criterio]) / (val_max - val_min)
                    else:
                        # Matemática para Benefício (Tradicional: o maior ganha nota 1)
                        df_ranking[f'{criterio}_Norm'] = (df_ranking[criterio] - val_min) / (val_max - val_min)
                        
                # Multiplica a nota normalizada pelo peso do AHP e soma no total do jogador
                df_ranking['Nota_Moneyball'] += df_ranking[f'{criterio}_Norm'] * peso

        # Convertendo a nota de 0-1 para 0-100 para ficar mais visual
        df_ranking['Nota_Moneyball'] = df_ranking['Nota_Moneyball'] * 100

        # Ordena do maior para o menor e remove as colunas normalizadas da exibição (deixando só o principal)
        df_final = df_posicao_limpo[['Jogador']].copy()
        df_final['Nota_Moneyball'] = df_ranking['Nota_Moneyball']
        df_final = df_final.sort_values(by='Nota_Moneyball', ascending=False)
        df_final['Equipe'] = df_posicao_limpo['Equipe']
        df_final['Valor estimado'] = df_posicao_limpo['Valor_Numerico']
        df_final['Idade'] = df_posicao_limpo['Idade']
        

        # Escolha as colunas para o Print final
        colunas_visualizacao = ['Jogador', 'Equipe' ,'Nota_Moneyball', 'Valor estimado', 'Idade']

        print("\n🏆 --- RANKING FINAL MONEYBALL (TOP 3 posicao) --- 🏆")
        # Arredonda a nota final para 2 casas decimais na hora de mostrar
        print(df_final[colunas_visualizacao].head(3).round({'Nota_Moneyball': 2}).to_string(index=False))
        return df_final[colunas_visualizacao]
    except Exception as e:
            return f"Erro ao processar: {e}"