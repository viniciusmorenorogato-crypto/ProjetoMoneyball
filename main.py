import pandas as pd
import warnings
import numpy as np
from Funções import valor
from Funções import data
from Funções import ahp

warnings.filterwarnings("ignore")

CRITERIOS_PADRAO = {
    '🧤Goleiros': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Altura', 'Contrato_Numerico',
            'Jogos completos', 'Expected Goals Prevented xGP', 'Falhas/90',
            '% Acerto do goleiro', 'Defesas totais / Jogo', 'Nota média'
        ],
        'nivel_1': ['Jogos completos', 'Falhas/90'],
        'nivel_2': ['Expected Goals Prevented xGP', 'Idade', 'Altura', 'Valor_Numerico', 'Salario_Numerico'],
    },
    '🧱Zagueiros': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Altura', 'Contrato_Numerico',
            'Jogos completos', '% Cabeceios Ganhos',
            'Rem Bloqueados, Interceptações  e Bloqueios/90', '% Des',
            'Desarmes Decisivos / 90', 'Acertos (Cabs, Des, Pres)', 'Acertos/90',
            'Bolas roubadas /90', '% Bolas disputadas e ganhas', 'Erros Defensivos /90',
            'Eficácia defensiva', 'Dist / 90', 'Nota média'
        ],
        'nivel_1': [
            'Desarmes Decisivos / 90', '% Bolas disputadas e ganhas', 'Acertos/90',
            'Eficácia defensiva', '% Cabeceios Ganhos', 'Nota média', 'Jogos completos'
        ],
        'nivel_2': [
            '% Des', 'Altura', 'Dist / 90',
            'Rem Bloqueados, Interceptações  e Bloqueios/90',
            'Acertos (Cabs, Des, Pres)', 'Valor_Numerico', 'Salario_Numerico', 'Idade'
        ],
    },
    '🛡️Laterais': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Altura', 'Jogos completos',
            'Participação / 90', 'Fintas / 90', 'Minutos pra criar uma chance de perigo',
            'Cruzamentos Conseguidos', 'xA + xG /90', 'Gols + A/90',
            'Movimentos ofensivos com sucesso', 'Dist / 90', 'Erros Defensivos /90',
            'Eficácia defensiva', 'Nota média'
        ],
        'nivel_1': [
            'Participação / 90', 'Minutos pra criar uma chance de perigo',
            'xA + xG /90', 'Eficácia defensiva', 'Nota média', 'Jogos completos'
        ],
        'nivel_2': [
            'Valor_Numerico', 'Salario_Numerico', 'Idade', 'Fintas / 90',
            'Gols + A/90', 'Movimentos ofensivos com sucesso'
        ],
    },
    '🛡️Volantes': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Jogos Completos',
            'Contrato_Numerico', 'Cartões por falta cometida', '% Pressão ganha/90',
            '% Bolas disputadas e ganhas (sem falta)', 'Passes certos  - errados / Jogo',
            'Passes em progressão/90', 'Eficácia defensiva', 'xA por passe decisivo',
            'Criação / 90', 'Distância /90', 'Nota média'
        ],
        'nivel_1': [
            'Eficácia defensiva', 'Passes certos  - errados / Jogo', 'xA por passe decisivo',
            'Criação / 90', '% Bolas disputadas e ganhas (sem falta)', 'Nota média', 'Jogos Completos'
        ],
        'nivel_2': [
            '% Pressão ganha/90', 'Passes em progressão/90', 'Distância /90',
            'Valor_Numerico', 'Salario_Numerico', 'Idade'
        ],
    },
    '🏃‍♂️Box-To-Box': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Jogos completos',
            'Contrato_Numerico', 'Taxa de Conversão %',
            'Participação por jogo (passes, fnt, fin, criação, roubadas de bola, etc)',
            '% Acerto', 'xA / Passe Decisivo', 'Dist / 90', 'Último terço/90', 'Nota média'
        ],
        'nivel_1': [
            'Taxa de Conversão %', 'xA / Passe Decisivo', 'Dist / 90',
            'Nota média', 'Jogos completos'
        ],
        'nivel_2': [
            'Participação por jogo (passes, fnt, fin, criação, roubadas de bola, etc)',
            '% Acerto', 'Último terço/90', 'Valor_Numerico', 'Salario_Numerico', 'Idade'
        ],
    },
    '🎯Armadores': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Jogos completos',
            'Contrato_Numerico', 'Gols+ Assist / 90', 'Fintas /90', 'non Pen xG /90',
            'xA /90', '% Cruzamentos certos', 'Passes Decisivos pra uma assistência',
            'xA / Passe Decisivo', 'Finalizações no gol/90',
            'Conversão dos chutes de fora da  área', 'Ações com Bola T/90',
            '% Sucesso de ações com bola', 'Ações que geraram finalizações ao gol /90',
            'Chances de perigo criadas /90',
            'Participação do jogador a cada 90 minutos (fnt, cabs, pass, finalizaçõs)',
            'Participação em passes / 90', 'Passes em construção de jog OF /90',
            'Ações no último terço / 90', 'Tentativas de marcar um gol / 90',
            'Dist / 90', 'Sprints/90', 'Nota média'
        ],
        'nivel_1': [
            'Gols+ Assist / 90', 'xA / Passe Decisivo',
            'Ações no último terço / 90', 'Nota média', 'Jogos completos'
        ],
        'nivel_2': [
            'Fintas /90', 'non Pen xG /90', '% Cruzamentos certos',
            'Passes Decisivos pra uma assistência', 'Tentativas de marcar um gol / 90',
            'Dist / 90', 'Valor_Numerico', 'Salario_Numerico', 'Idade'
        ],
    },
    '⚽Avançados': {
        'colunas': [
            'Valor_Numerico', 'Idade', 'Salario_Numerico', 'Jogos completos',
            'Contrato_Numerico', 'Média de gols em toda a Carreira', 'Média gols / partida',
            'Média gols + ass / partida', 'Gols Sem Pênalti /90', 'Gols de dentro da área /90',
            'Gols de fora da área /90', '% Cabs ganhos', 'Impedimentos / 90',
            'Finalizações no gol/90', 'GPI (Goal Probability Index)',
            'Over xG / Under xG per 90', 'Minutos pra acertar uma finalização no gol',
            'Minutos pra MARCAR um gol', 'Minutos pra PARTICIPAR de um gol',
            'Gols não esperados SEM PÊNALTI', 'xG Conclusion', 'Pass D /90',
            'Fintas/90', '% Des + Pressões concluídas', 'Dist / 90',
            'Eficácia ofensiva', 'Participação do jogador a cada 90 minutos',
            '% Sucesso de ações com bola', 'Tentativas de marcar um gol  /90', 'Nota média'
        ],
        'nivel_1': [
            'Média de gols em toda a Carreira', 'Média gols / partida', 'Nota média',
            'Valor_Numerico', 'Salario_Numerico', 'Jogos completos',
            'GPI (Goal Probability Index)'
        ],
        'nivel_2': [
            'Gols Sem Pênalti /90', 'Gols de dentro da área /90', 'Gols de fora da área /90',
            '% Cabs ganhos', 'Finalizações no gol/90', 'Minutos pra MARCAR um gol',
            'xG Conclusion', 'Pass D /90', 'Fintas/90', 'Dist / 90',
            'Eficácia ofensiva', 'Participação do jogador a cada 90 minutos'
        ],
    },
}

CRITERIOS_DE_CUSTO = [
    'Valor_Numerico', 'Salario_Numerico', 'Falhas/90', 'Idade', 'Contrato_Numerico',
    'Erros Defensivos /90', 'Minutos pra criar uma chance de perigo',
    'Cartões por falta cometida', 'Minutos pra acertar uma finalização no gol',
    'Minutos pra MARCAR um gol', 'Minutos pra PARTICIPAR de um gol', 'Impedimentos / 90'
]

COLUNA_VALOR_POR_POSICAO = {
    '🧤Goleiros':     'Valor estimado',
    '🧱Zagueiros':    'Valor',
    '🛡️Laterais':    'Valor Estimado',
    '🛡️Volantes':    'Valor',
    '🏃‍♂️Box-To-Box': 'Valor',
    '🎯Armadores':    'Valor',
    '⚽Avançados':    'Valor Estimado',
}

COLUNA_CONTRATO_POR_POSICAO = {
    '🛡️Volantes':     'Data Final de Contrato',
    '🏃‍♂️Box-To-Box':  'Fim de contrato',
    '🎯Armadores':    'Data Final do contrato',
    '⚽Avançados':    'Data Final do contrato',
}

MIN_CRITERIOS_ATIVOS = 2  # mínimo de critérios para o AHP fazer sentido


def gerar_ranking(df_bruto, posicao, niveis_usuario=None):
    """
    Calcula o ranking Moneyball para uma posição.

    niveis_usuario: dict { criterio: 0|1|2|3 }
                    0 = Ignorar (excluído), 1/2/3 = níveis AHP.
                    None = usa padrão do CRITERIOS_PADRAO.

    Retorna: DataFrame com colunas [Jogador, Equipe, Nota_Moneyball, Valor estimado, Idade]
             ou lança ValueError com mensagem amigável em caso de erro recuperável.
    """
    # ── 1. Validação de entrada ────────────────────────────────────────────────
    if posicao not in CRITERIOS_PADRAO:
        raise ValueError(f"Posição '{posicao}' não reconhecida pelo sistema.")

    if df_bruto is None or df_bruto.empty:
        raise ValueError(f"A aba '{posicao}' está vazia na planilha.")

    # ── 2. Corte e limpeza do DataFrame ───────────────────────────────────────
    try:
        df = df_bruto.loc[:, 'Jogador':'Nota média'].copy()
    except KeyError:
        raise ValueError(
            f"Não foi possível localizar as colunas 'Jogador' e/ou 'Nota média' "
            f"na aba '{posicao}'. Verifique se a planilha está no formato correto."
        )

    df = df.dropna(subset=[df.columns[0]])
    if df.empty:
        raise ValueError(f"Nenhum jogador encontrado na aba '{posicao}' após remover linhas vazias.")

    # ── 3. Valor de mercado ────────────────────────────────────────────────────
    nome_col_valor = COLUNA_VALOR_POR_POSICAO.get(posicao, 'Valor estimado')
    if nome_col_valor not in df.columns:
        raise ValueError(
            f"Coluna de valor '{nome_col_valor}' não encontrada na aba '{posicao}'."
        )

    df['Valor_Numerico'] = df[nome_col_valor].apply(valor.limpar_valor_mercado)
    valores_positivos = df[df['Valor_Numerico'] > 0]['Valor_Numerico']

    if valores_positivos.empty:
        # Todos inegociáveis ou inválidos — usa fallback neutro
        df['Valor_Numerico'] = 0.0
    else:
        val_max_real = valores_positivos.max()
        val_min_real = valores_positivos.min()
        df.loc[df['Valor_Numerico'] == -1, 'Valor_Numerico'] = val_max_real * 2
        df.loc[df['Valor_Numerico'] == -2, 'Valor_Numerico'] = val_min_real + (val_max_real + val_min_real) / 2

    # ── 4. Salário ─────────────────────────────────────────────────────────────
    if 'Salário' not in df.columns:
        df['Salario_Numerico'] = 0.0
    else:
        df['Salario_Numerico'] = df['Salário'].apply(valor.limpar_salario)

    # ── 5. Contrato ────────────────────────────────────────────────────────────
    nome_col_contrato = COLUNA_CONTRATO_POR_POSICAO.get(posicao, 'Data final de contrato')
    if nome_col_contrato in df.columns:
        df['Contrato_Numerico'] = df[nome_col_contrato].apply(data.limpar_data_contrato)

    # ── 6. Critérios e níveis ──────────────────────────────────────────────────
    padrao = CRITERIOS_PADRAO[posicao]
    colunas_para_ver = [c for c in padrao['colunas'] if c in df.columns]

    if niveis_usuario:
        ignorados   = {c for c, n in niveis_usuario.items() if n == 0}
        nivel_1     = [c for c, n in niveis_usuario.items() if n == 1 and c in df.columns and c not in ignorados]
        nivel_2     = [c for c, n in niveis_usuario.items() if n == 2 and c in df.columns and c not in ignorados]
        nivel_3     = [c for c, n in niveis_usuario.items() if n == 3 and c in df.columns and c not in ignorados]
        colunas_para_ver = [c for c in colunas_para_ver if c not in ignorados]

        ativos = nivel_1 + nivel_2 + nivel_3
        if len(ativos) < MIN_CRITERIOS_ATIVOS:
            raise ValueError(
                f"São necessários pelo menos {MIN_CRITERIOS_ATIVOS} critérios ativos "
                f"para calcular o ranking de {posicao}. "
                f"Você marcou todos como 'Ignorar' ou deixou menos de {MIN_CRITERIOS_ATIVOS} ativos."
            )
    else:
        nivel_1 = [c for c in padrao['nivel_1'] if c in df.columns]
        nivel_2 = [c for c in padrao['nivel_2'] if c in df.columns]
        nivel_3 = [c for c in df.columns if c not in nivel_1 and c not in nivel_2]

    if not colunas_para_ver:
        raise ValueError(
            f"Nenhuma coluna de critério encontrada na aba '{posicao}'. "
            f"Verifique se os nomes das colunas da planilha estão corretos."
        )

    def obter_nivel(criterio):
        if criterio in nivel_1: return 1
        if criterio in nivel_2: return 2
        return 3

    criterios = nivel_1 + nivel_2 + nivel_3
    n = len(criterios)

    if n == 0:
        raise ValueError(f"Nenhum critério ativo para calcular o ranking de {posicao}.")

    # ── 7. Matriz AHP ──────────────────────────────────────────────────────────
    matriz_saaty = np.ones((n, n))  # diagonal 1 por padrão
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            t_i = obter_nivel(criterios[i])
            t_j = obter_nivel(criterios[j])
            if   t_i == 1 and t_j == 2: v = 2.0
            elif t_i == 1 and t_j == 3: v = 9.0
            elif t_i == 2 and t_j == 3: v = 5.0
            elif t_i == 2 and t_j == 1: v = 1/2
            elif t_i == 3 and t_j == 1: v = 1/9
            elif t_i == 3 and t_j == 2: v = 1/5
            else: v = 1.0
            matriz_saaty[i, j] = v

    try:
        pesos, cr, consistente = ahp.calcular_pesos_ahp(matriz_saaty)
    except Exception as e:
        raise ValueError(f"Erro no cálculo AHP para {posicao}: {e}")

    if pesos is None or len(pesos) != n:
        raise ValueError(f"O cálculo AHP retornou pesos inválidos para {posicao}.")

    # ── 8. Ranking ─────────────────────────────────────────────────────────────
    df_ranking = df[colunas_para_ver].copy()

    # Garante que todas as colunas de critério são numéricas
    for col in colunas_para_ver:
        df_ranking[col] = pd.to_numeric(df_ranking[col], errors='coerce').fillna(0)

    df_ranking['Nota_Moneyball'] = 0.0

    for criterio, peso in zip(criterios, pesos):
        if criterio not in df_ranking.columns:
            continue
        vmax = df_ranking[criterio].max()
        vmin = df_ranking[criterio].min()
        if vmax == vmin:
            df_ranking[f'{criterio}_Norm'] = 0.0
        elif criterio in CRITERIOS_DE_CUSTO:
            df_ranking[f'{criterio}_Norm'] = (vmax - df_ranking[criterio]) / (vmax - vmin)
        else:
            df_ranking[f'{criterio}_Norm'] = (df_ranking[criterio] - vmin) / (vmax - vmin)
        df_ranking['Nota_Moneyball'] += df_ranking[f'{criterio}_Norm'] * peso

    df_ranking['Nota_Moneyball'] *= 100

    # ── 9. Resultado ───────────────────────────────────────────────────────────
    df_final = pd.DataFrame()
    df_final['Jogador']        = df['Jogador'].values
    df_final['Nota_Moneyball'] = df_ranking['Nota_Moneyball'].values
    df_final['Equipe']         = df['Equipe'].values if 'Equipe' in df.columns else '—'
    df_final['Valor estimado'] = df['Valor_Numerico'].values
    df_final['Idade']          = pd.to_numeric(df['Idade'], errors='coerce').values if 'Idade' in df.columns else 0

    df_final = df_final.sort_values(by='Nota_Moneyball', ascending=False).reset_index(drop=True)

    return df_final[['Jogador', 'Equipe', 'Nota_Moneyball', 'Valor estimado', 'Idade']]