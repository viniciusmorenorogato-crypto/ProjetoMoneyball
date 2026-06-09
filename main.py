import pandas as pd
import warnings
import numpy as np
from Funções import valor
from Funções import data
from Funções import ahp

warnings.filterwarnings("ignore")

def gerar_ranking(df_bruto, posicao):

    # ==========================================
    # 1. CARREGAMENTO DA PLANILHA
    # ==========================================

    try:
        try:
            
            df_posicao_limpo = df_bruto.loc[:, 'Jogador':'Nota média']
            
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

        if posicao == '🧤Goleiros':
            nome_coluna_valor = 'Valor estimado'
        elif posicao == '🧱Zagueiros':
            nome_coluna_valor = 'Valor'
        elif posicao == '🛡️Laterais':
            nome_coluna_valor = 'Valor Estimado'
        elif posicao == '🛡️Volantes':
            nome_coluna_valor = 'Valor'
        elif posicao == '🏃‍♂️Box-To-Box':
            nome_coluna_valor = 'Valor'
        elif posicao == '🎯Armadores':
            nome_coluna_valor = 'Valor'
        elif posicao == '⚽Avançados':
            nome_coluna_valor = 'Valor Estimado'

        # Aplica a limpeza chamando a função do arquivo minhas_funcoes.py
        df_posicao_limpo['Valor_Numerico'] = df_posicao_limpo[nome_coluna_valor].apply(valor.limpar_valor_mercado)

        # Encontra o valor máximo verdadeiro da coluna (ignorando os -1 temporários)
        valor_maximo_real = df_posicao_limpo[df_posicao_limpo['Valor_Numerico'] > 0]['Valor_Numerico'].max()
        valor_minimo_real = df_posicao_limpo[df_posicao_limpo['Valor_Numerico'] > 0]['Valor_Numerico'].min()

        # Substitui todos os inegociáveis (-1) pelo (valor_maximo_real * 2)
        novo_valor_inegociaveis = valor_maximo_real * 2
        df_posicao_limpo.loc[df_posicao_limpo['Valor_Numerico'] == -1, 'Valor_Numerico'] = novo_valor_inegociaveis
        df_posicao_limpo.loc[df_posicao_limpo['Valor_Numerico'] == -2, 'Valor_Numerico'] = valor_minimo_real + (valor_maximo_real + valor_minimo_real) / 2

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

        if posicao in ['🛡️Volantes']:
            nome_coluna_contrato = 'Data Final de Contrato' # ou o nome exato que estiver na sua planilha
        elif posicao in ['🏃‍♂️Box-To-Box']:
            nome_coluna_contrato = 'Fim de contrato' # ou o nome exato que estiver na sua planilha
        elif posicao in ['🎯Armadores']:
            nome_coluna_contrato = 'Data Final do contrato' # ou o nome exato que estiver na sua planilha
        elif posicao in ['⚽Avançados']:        
            nome_coluna_contrato = 'Data Final do contrato' # ou o nome exato que estiver na sua planilha
        else:
            nome_coluna_contrato = 'Data final de contrato' # ou o nome exato que estiver na sua planilha 

        # Verifica se a coluna realmente existe na aba atual (ex: os Laterais não têm)
        if nome_coluna_contrato in df_posicao_limpo.columns:
            df_posicao_limpo['Contrato_Numerico'] = df_posicao_limpo[nome_coluna_contrato].apply(data.limpar_data_contrato)
        else:
            # Se a coluna não existir, o Python ignora o tratamento e segue a vida!
            pass
        # ==========================================
        # 5. EXPORTAR PARA UMA NOVA PLANILHA
        # ==========================================

        if posicao == '🧤Goleiros':
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
        elif posicao == '🧱Zagueiros':
            colunas_para_ver = ['Valor_Numerico', 
                                'Idade', 
                                'Salario_Numerico', 
                                'Altura', 
                                'Contrato_Numerico',
                                'Jogos completos',
                                '% Cabeceios Ganhos',
                                'Rem Bloqueados, Interceptações  e Bloqueios/90',
                                '% Des',
                                'Desarmes Decisivos / 90',
                                'Acertos (Cabs, Des, Pres)',
                                'Acertos/90',
                                'Bolas roubadas /90',
                                '% Bolas disputadas e ganhas',
                                'Erros Defensivos /90',
                                'Eficácia defensiva',
                                'Dist / 90',
                                'Nota média'
                                ]
        elif posicao == '🛡️Laterais':
            colunas_para_ver = ['Valor_Numerico', 
                                'Idade', 
                                'Salario_Numerico', 
                                'Altura', 
                                'Jogos completos',
                                'Participação / 90',
                                'Fintas / 90',
                                'Minutos pra criar uma chance de perigo',
                                'Cruzamentos Conseguidos',
                                'xA + xG /90',
                                'Gols + A/90',
                                'Movimentos ofensivos com sucesso',
                                'Dist / 90',
                                'Erros Defensivos /90',
                                'Eficácia defensiva',
                                'Nota média'
                                ]
        elif posicao == '🛡️Volantes':
            colunas_para_ver = ['Valor_Numerico', 
                                'Idade', 
                                'Salario_Numerico', 
                                'Jogos Completos',
                                'Contrato_Numerico',
                                'Cartões por falta cometida',
                                '% Pressão ganha/90',
                                '% Bolas disputadas e ganhas (sem falta)',
                                'Passes certos  - errados / Jogo',
                                'Passes em progressão/90',
                                'Eficácia defensiva',
                                'xA por passe decisivo',
                                'Criação / 90',
                                'Distância /90',
                                'Nota média'
                                ]
        elif posicao == '🏃‍♂️Box-To-Box':
            colunas_para_ver = ['Valor_Numerico', 
                                'Idade', 
                                'Salario_Numerico', 
                                'Jogos completos',
                                'Contrato_Numerico',
                                'Taxa de Conversão %',
                                'Participação por jogo (passes, fnt, fin, criação, roubadas de bola, etc)',
                                '% Acerto',
                                'xA / Passe Decisivo',
                                'Dist / 90',
                                'Último terço/90',
                                'Nota média'
                                ]
        elif posicao == '🎯Armadores':
            colunas_para_ver = ['Valor_Numerico', 
                                'Idade', 
                                'Salario_Numerico', 
                                'Jogos completos',
                                'Contrato_Numerico',
                                'Gols+ Assist / 90',
                                'Fintas /90',
                                'non Pen xG /90',
                                'xA /90',
                                '% Cruzamentos certos',
                                'Passes Decisivos pra uma assistência',
                                'xA / Passe Decisivo',
                                'Finalizações no gol/90',
                                'Conversão dos chutes de fora da  área',
                                'Ações com Bola T/90',
                                '% Sucesso de ações com bola',
                                'Ações que geraram finalizações ao gol /90',
                                'Chances de perigo criadas /90',
                                'Participação do jogador a cada 90 minutos (fnt, cabs, pass, finalizaçõs)',
                                'Participação em passes / 90',
                                'Passes em construção de jog OF /90',
                                'Ações no último terço / 90',
                                'Tentativas de marcar um gol / 90',
                                'Dist / 90',
                                'Sprints/90',
                                'Nota média'
                                ]
        elif posicao == '⚽Avançados':
            colunas_para_ver = ['Valor_Numerico', 
                                'Idade', 
                                'Salario_Numerico', 
                                'Jogos completos',
                                'Contrato_Numerico',
                                'Média de gols em toda a Carreira',
                                'Média gols / partida',
                                'Média gols + ass / partida',
                                'Gols Sem Pênalti /90',
                                'Gols de dentro da área /90',
                                'Gols de fora da área /90',
                                '% Cabs ganhos',
                                'Impedimentos / 90',
                                'Finalizações no gol/90',
                                'GPI (Goal Probability Index)',
                                'Over xG / Under xG per 90',
                                'Minutos pra acertar uma finalização no gol',
                                'Minutos pra MARCAR um gol',
                                'Minutos pra PARTICIPAR de um gol',
                                'Gols não esperados SEM PÊNALTI',
                                'xG Conclusion',
                                'Pass D /90',
                                'Fintas/90',
                                '% Des + Pressões concluídas',
                                'Dist / 90',
                                'Eficácia ofensiva',
                                'Participação do jogador a cada 90 minutos',
                                '% Sucesso de ações com bola',
                                'Tentativas de marcar um gol  /90',
                                'Nota média']
        # ==========================================
        # 6. ONDE O FILHO CHORA E O PAI NÃO VÊ: AHP PARA DEFINIR OS PESOS DOS CRITÉRIOS
        # ==========================================
        if posicao == '🧤Goleiros':
            nivel_1 = ['Jogos Completos', 'Falhas/90']
            nivel_2 = [ 
                'Expected Goals Prevented xGP',
                'Idade', 
                'Altura',
                'Valor_Numerico',
                'Salario_Numerico',                 
            ]
            nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]
        elif posicao == '🧱Zagueiros':
            nivel_1 = ['Desarmes Decisivos / 90',
                       '% Bolas disputadas e ganhas', 
                       'Acertos/90',
                       'Eficácia defensiva',
                       '% Cabeceios Ganhos',
                       'Nota média',
                       'Jogos completos'
                       ]
            nivel_2 = [
                '% Des',
                'Altura',
                'Dist / 90', 
                'Rem Bloqueados, Interceptações  e Bloqueios/90',
                'Acertos (Cabs, Des, Pres)',
                'Valor_Numerico',
                'Salario_Numerico',
                'Idade'
            ]
            nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]
        elif posicao == '🛡️Laterais':
            nivel_1 = ['Participação / 90',
                       'Minutos pra criar uma chance de perigo',
                       'xA + xG /90',
                       'Eficácia defensiva',
                       'Nota média',
                       'Jogos completos'
                       ]
            nivel_2 = [
                'Valor_Numerico',
                'Salario_Numerico',
                'Idade',
                'Fintas / 90',
                'Gols + A/90',
                'Movimentos ofensivos com sucesso',
            ]
            nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]
        elif posicao == '🛡️Volantes':
            nivel_1 = ['Eficácia defensiva',
                       'Passes certos  - errados / Jogo',
                       'xA por passe decisivo',
                       'Criação / 90',
                       '% Bolas disputadas e ganhas (sem falta)',
                       'Nota média',
                       'Jogos Completos'
                       ]
            nivel_2 = [
                '% Pressão ganha/90',
                'Passes em progressão/90',
                'Distância /90',
                'Valor_Numerico',
                'Salario_Numerico',
                'Idade',
            ]
            nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]
        elif posicao == '🏃‍♂️Box-To-Box':
            nivel_1 = ['Taxa de Conversão %',
                       'xA / Passe Decisivo',
                       'Dist / 90',
                       'Nota média',
                       'Jogos completos'
                       ]
            nivel_2 = [
                'Participação por jogo (passes, fnt, fin, criação, roubadas de bola, etc)',
                '% Acerto',
                'Último terço/90',
                'Valor_Numerico',
                'Salario_Numerico',
                'Idade',
            ]
            nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]
        elif posicao == '🎯Armadores':
            nivel_1 = ['Gols+ Assist / 90',
                       'xA / Passe Decisivo',
                       'Ações no último terço / 90',
                       'Nota média',
                       'Jogos completos'
                       ]
            nivel_2 = [
                'Fintas /90',
                'non Pen xG /90',
                '% Cruzamentos certos',
                'Passes Decisivos pra uma assistência',
                'Tentativas de marcar um gol / 90',
                'Dist / 90',
                'Valor_Numerico',
                'Salario_Numerico',
                'Idade',
            ]
            nivel_3 = [col for col in df_posicao_limpo.columns if col not in nivel_1 and col not in nivel_2]
        elif posicao == '⚽Avançados':
            nivel_1 = ['Média de gols em toda a Carreira',
                       'Média gols / partida',
                       'Nota média',
                       'Valor_Numerico',
                       'Salario_Numerico',
                       'Jogos completos',
                       'GPI (Goal Probability Index)'
                       ]
            nivel_2 = [
                'Gols Sem Pênalti /90',
                'Gols de dentro da área /90',
                'Gols de fora da área /90',
                '% Cabs ganhos',
                'Finalizações no gol/90',
                'GPI (Goal Probability Index)',
                'Minutos pra MARCAR um gol',
                'xG Conclusion',
                'Pass D /90',
                'Fintas/90',
                'Dist / 90',
                'Eficácia ofensiva',
                'Participação do jogador a cada 90 minutos',
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

        # ==========================================
        # 7. AQUI O FILHO TERMINA DE CHORAR: REALIZAÇÃO DO RANKING FINAL COM BASE NOS PESOS DO AHP
        # ==========================================

        criterios_de_custo = [
            'Valor_Numerico', 
            'Salario_Numerico', 
            'Falhas/90',
            'Idade',
            'Contrato_Numerico',
            'Erros Defensivos /90',
            'Minutos pra criar uma chance de perigo',
            'Cartões por falta cometida',
            'Minutos pra acertar uma finalização no gol',
            'Minutos pra MARCAR um gol',
            'Minutos pra PARTICIPAR de um gol',
            'Impedimentos / 90'
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
        print(f"\nNota Moneyball calculada! Exibindo a nota de cada jogador:")
        print(df_final[['Jogador', 'Nota_Moneyball']].head(50))

        return df_final[colunas_visualizacao]
    except Exception as e:
            return f"Erro ao processar: {e}"
        
# Bloco de teste direto
# if __name__ == "__main__":
#     import pandas as pd
    
#     print("Iniciando depuração isolada...")
#     # 1. Lê a sua planilha local bruta
#     banco_completo = pd.read_excel("Moneyball FM26.xlsm", engine='openpyxl')
    
#     # 2. Chama a sua função simulando o que o app.py faria
#     resultado = gerar_ranking(banco_completo, posicao='🎯Armadores')
    
#     print("Fim da depuração!")