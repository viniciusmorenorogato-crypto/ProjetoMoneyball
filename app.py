import streamlit as st
import pandas as pd
import main
import google.generativeai as genai
import altair as alt
import math

st.set_page_config(
    page_title="Scout Moneyball",
    page_icon=":material/sports_soccer:",
    layout="wide",
)

# ==========================================
# SESSION STATE
# ==========================================
if 'ja_calculou' not in st.session_state:
    st.session_state['ja_calculou'] = False

# ==========================================
# SIDEBAR — original, sem modificações
# ==========================================
st.sidebar.title("⚙️ Configurações")

posicao_analise = st.sidebar.selectbox(
    "Selecione a Posição para Análise:",
    ['🧤Goleiros', '🧱Zagueiros', '🛡️Laterais', '🛡️Volantes', '🏃‍♂️Box-To-Box', '🎯Armadores', '⚽Avançados'],
    disabled=st.session_state['ja_calculou']
)

arquivo_upload = st.sidebar.file_uploader(
    "Arraste a sua planilha Moneyball aqui (.xlsx ou .xlsm)",
    type=["xlsx", "xlsm"],
    disabled=st.session_state['ja_calculou']
)

col_btn1, col_btn2 = st.sidebar.columns(2)

if arquivo_upload is not None:
    if col_btn1.button("🚀 Calcular", disabled=st.session_state['ja_calculou'], use_container_width=True):
        with st.spinner(f"Processando {posicao_analise}..."):
            if 'banco_de_dados_completo' not in st.session_state:
                st.session_state['banco_de_dados_completo'] = pd.read_excel(
                    arquivo_upload, sheet_name=None, engine='openpyxl'
                )
                st.sidebar.success("Base de dados carregada com sucesso!")
            df_aba = st.session_state['banco_de_dados_completo'][posicao_analise]
            tabela_processada = main.gerar_ranking(df_aba, posicao_analise)
            st.session_state['dados_salvos'] = tabela_processada
            st.session_state['posicao_salva'] = posicao_analise
            if 'relatorio_ia_salvo' in st.session_state:
                del st.session_state['relatorio_ia_salvo']
            st.session_state['ja_calculou'] = True
            st.rerun()

if st.session_state['ja_calculou']:
    if col_btn2.button("🔄 Recomeçar", use_container_width=True):
        for key in ['ja_calculou', 'dados_salvos', 'relatorio_ia_salvo', 'banco_de_dados_completo', 'posicao_salva']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state['ja_calculou'] = False
        st.rerun()

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
if arquivo_upload is None and not st.session_state['ja_calculou']:
    st.info("👈 Comece fazendo o upload da sua planilha na barra lateral!")
    st.stop()

if arquivo_upload is not None and 'banco_de_dados_completo' not in st.session_state:
    with st.spinner("Carregando toda a base de dados do FM para a memória..."):
        st.session_state['banco_de_dados_completo'] = pd.read_excel(
            arquivo_upload, sheet_name=None, engine='openpyxl'
        )
        st.sidebar.success("Base de dados carregada com sucesso!")

if 'dados_salvos' not in st.session_state:
    st.info("Selecione a posição e clique em **🚀 Calcular** para gerar os rankings.")
    st.stop()

# ==========================================
# DADOS
# ==========================================
posicao_analise = st.session_state.get('posicao_salva', posicao_analise)
df_resultado = st.session_state['dados_salvos'].copy()
banco_completo = st.session_state['banco_de_dados_completo']
df_da_posicao = banco_completo[posicao_analise].copy()

COLUNAS_POR_POSICAO = {
    '🧤Goleiros': ['Jogador', 'Equipe', 'Valor estimado', 'Idade', 'Salário', 'Altura',
                   'Data final de contrato', 'Jogos completos', 'Expected Goals Prevented xGP',
                   'Falhas/90', '% Acerto do goleiro', 'Defesas totais / Jogo', 'Nota média'],
    '🧱Zagueiros': ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Altura',
                    'Data final de contrato', 'Jogos completos', 'Desarmes Decisivos / 90',
                    'Acertos (Cabs, Des, Pres)', 'Acertos/90', 'Bolas roubadas /90',
                    '% Bolas disputadas e ganhas', 'Erros Defensivos /90', 'Eficácia defensiva', 'Nota média'],
    '🛡️Laterais': ['Jogador', 'Equipe', 'Valor Estimado', 'Idade', 'Salário', 'Altura',
                    'Jogos completos', 'Participação / 90', 'Fintas / 90',
                    'Minutos pra criar uma chance de perigo', 'Cruzamentos Conseguidos',
                    'xA + xG /90', 'Gols + A/90', 'Movimentos ofensivos com sucesso',
                    'Dist / 90', 'Erros Defensivos /90', 'Eficácia defensiva', 'Nota média'],
    '🛡️Volantes': ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Jogos Completos',
                    'Data Final de Contrato', 'Cartões por falta cometida',
                    '% Pressão ganha/90', '% Bolas disputadas e ganhas (sem falta)',
                    'Passes certos  - errados / Jogo', 'Passes em progressão/90',
                    'Eficácia defensiva', 'xA por passe decisivo', 'Criação / 90',
                    'Distância /90', 'Nota média'],
    '🏃‍♂️Box-To-Box': ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Jogos completos',
                      'Fim de contrato', 'Taxa de Conversão %',
                      'Participação por jogo (passes, fnt, fin, criação, roubadas de bola, etc)',
                      '% Acerto', 'xA / Passe Decisivo', 'Dist / 90', 'Último terço/90', 'Nota média'],
    '🎯Armadores': ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Jogos completos',
                    'Data Final do contrato', 'Gols+ Assist / 90', 'Fintas /90',
                    'non Pen xG /90', 'xA /90', '% Cruzamentos certos',
                    'Passes Decisivos pra uma assistência', 'xA / Passe Decisivo',
                    'Finalizações no gol/90', 'Ações com Bola T/90', '% Sucesso de ações com bola',
                    'Dist / 90', 'Nota média'],
    '⚽Avançados': ['Jogador', 'Equipe', 'Valor Estimado', 'Idade', 'Salário', 'Jogos completos',
                    'Data Final do contrato', 'Gols Sem Pênalti /90', 'Gols de dentro da área /90',
                    'Finalizações no gol/90', 'GPI (Goal Probability Index)',
                    'Over xG / Under xG per 90', 'Minutos pra MARCAR um gol',
                    'Gols não esperados SEM PÊNALTI', 'Fintas/90', 'Eficácia ofensiva', 'Nota média'],
}

colunas_para_juntar = COLUNAS_POR_POSICAO.get(posicao_analise, ['Jogador', 'Equipe', 'Idade', 'Nota média'])
colunas_existentes = [c for c in colunas_para_juntar if c in df_da_posicao.columns]

df_resultados = df_da_posicao[colunas_existentes].copy()
df_resultados['Nota_Moneyball'] = df_resultado['Nota_Moneyball'].values
df_resultados = df_resultados.sort_values(by='Nota_Moneyball', ascending=False).reset_index(drop=True)
df_filtrado = df_resultados.copy()

if df_filtrado.empty:
    st.warning("Nenhum jogador encontrado com esses filtros. Aumente o orçamento ou a idade!")
    st.stop()

alvo = df_filtrado.iloc[0]
colunas_numericas = df_filtrado.select_dtypes(include=['float64', 'int64']).columns.tolist()

# ==========================================
# TÍTULO
# ==========================================
st.title(f"🏆 Moneyball — {posicao_analise}")

# ==========================================
# ABAS
# ==========================================
tab_dashboard, tab_comparativo, tab_scout = st.tabs([
    ":material/dashboard: Dashboard",
    ":material/bar_chart: Comparativo",
    ":material/smart_toy: Olheiro IA",
])

# ==========================================
# ABA 1: DASHBOARD
# ==========================================
with tab_dashboard:

    # Principal alvo — KPI cards
    st.subheader("🥇 Principal alvo de acordo com a nota Moneyball")
    with st.container(horizontal=True):
        st.metric("Melhor contratação", alvo['Jogador'],
                  delta=f"Nota: {alvo['Nota_Moneyball']:.1f}/100", border=True)
        val_col = next((c for c in ['Valor estimado', 'Valor Estimado', 'Valor'] if c in alvo.index), None)
        if val_col:
            val = alvo[val_col]
            if isinstance(val, (int, float)) and not math.isnan(val):
                st.metric("Valor estimado", f"€ {val/1_000_000:.1f}M", border=True)
        st.metric("Idade", f"{int(alvo['Idade'])} anos", border=True)
        sal_col = next((c for c in ['Salário'] if c in alvo.index), None)
        if sal_col:
            sal = alvo[sal_col]
            if isinstance(sal, (int, float)) and not math.isnan(sal):
                st.metric("Salário", f"€ {sal/1_000:.0f}k/mês", border=True)

    st.space("medium")

    # Top 10 + distribuição
    st.subheader("🏆 Top 10 recomendados")
    col_lista, col_dist = st.columns([1, 2], gap="medium")

    with col_lista:
        with st.container(border=True, height=440):
            for i, row in enumerate(df_filtrado.head(10).itertuples(), 1):
                medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"**{i}º**")
                st.markdown(f"{medalha} {row.Jogador}")
                st.caption(f"Nota: {row.Nota_Moneyball:.1f} · {int(row.Idade)} anos")
                if i < 10:
                    st.divider()

    with col_dist:
        with st.container(border=True, height=440):
            st.markdown("**Notas Moneyball por jogador**")
            chart_dist = alt.Chart(df_filtrado.head(10)).mark_bar(
                color='#22C55E', cornerRadiusEnd=3
            ).encode(
                x=alt.X('Nota_Moneyball:Q', title='Nota Moneyball'),
                y=alt.Y('Jogador:N', sort='-x', title=''),
                tooltip=['Jogador', 'Equipe', alt.Tooltip('Nota_Moneyball:Q', title='Nota', format='.1f')]
            ).properties(height=360)
            st.altair_chart(chart_dist)

    # Scatter Nota Moneyball × Nota média
    st.space("medium")
    st.subheader("📊 Nota Moneyball vs Nota média FM")
    with st.container(border=True):
        if 'Nota média' in df_filtrado.columns:
            scatter = alt.Chart(df_filtrado).mark_circle(size=90, opacity=0.8).encode(
                x=alt.X('Nota_Moneyball:Q', title='Nota Moneyball', scale=alt.Scale(zero=False)),
                y=alt.Y('Nota média:Q', title='Nota média FM', scale=alt.Scale(zero=False)),
                color=alt.Color('Nota_Moneyball:Q', scale=alt.Scale(scheme='greens'), legend=None),
                tooltip=['Jogador', 'Equipe',
                         alt.Tooltip('Nota_Moneyball:Q', title='Nota Moneyball', format='.1f'),
                         alt.Tooltip('Nota média:Q', title='Nota média FM', format='.1f')]
            ).properties(height=340)
            labels = scatter.mark_text(dy=-10, fontSize=11).encode(text='Jogador:N')
            st.altair_chart(scatter + labels)
        else:
            st.caption("Coluna 'Nota média' não encontrada para esta posição.")

    # Tabela completa
    st.space("medium")
    st.subheader("📋 Relatório completo — Top 10")

    col_config_tabela = {
        'Nota_Moneyball': st.column_config.ProgressColumn(
            'Nota Moneyball', min_value=0, max_value=100, format='%.1f'
        ),
    }
    if 'Nota média' in df_filtrado.columns:
        col_config_tabela['Nota média'] = st.column_config.ProgressColumn(
            'Nota média FM', min_value=0, max_value=20, format='%.1f'
        )

    st.dataframe(df_filtrado.head(10), column_config=col_config_tabela, hide_index=True)

# ==========================================
# ABA 2: COMPARATIVO
# ==========================================
with tab_comparativo:

    jogadores_disponiveis = df_filtrado['Jogador'].tolist()

    col_ctrl, col_charts = st.columns([1, 2], gap="medium")

    with col_ctrl:
        with st.container(border=True):
            st.markdown("**Selecione jogadores**")
            selecionados = st.multiselect(
                "Até 5 jogadores:",
                options=jogadores_disponiveis,
                default=jogadores_disponiveis[:3],
                max_selections=5
            )
            atributo_barra = st.selectbox(
                "Atributo para comparar:",
                colunas_numericas,
                index=colunas_numericas.index('Nota_Moneyball') if 'Nota_Moneyball' in colunas_numericas else 0,
                key="atrib_barra"
            )
            atributo_x = st.selectbox(
                "Scatter — Eixo X:",
                colunas_numericas,
                index=colunas_numericas.index('Nota_Moneyball') if 'Nota_Moneyball' in colunas_numericas else 0,
                key="eixo_x"
            )
            atributo_y = st.selectbox(
                "Scatter — Eixo Y:",
                colunas_numericas,
                index=min(1, len(colunas_numericas) - 1),
                key="eixo_y"
            )

    with col_charts:
        if selecionados:
            df_comp = df_filtrado[df_filtrado['Jogador'].isin(selecionados)]

            with st.container(border=True):
                st.markdown(f"**Ranking: {atributo_barra}**")
                grafico_barras = alt.Chart(df_comp).mark_bar(cornerRadiusEnd=4).encode(
                    x=alt.X(f'{atributo_barra}:Q', title=atributo_barra),
                    y=alt.Y('Jogador:N', sort='-x', title=''),
                    color=alt.Color(f'{atributo_barra}:Q', scale=alt.Scale(scheme='greens'), legend=None),
                    tooltip=['Jogador', alt.Tooltip(f'{atributo_barra}:Q', format='.2f')]
                ).properties(height=200)
                st.altair_chart(grafico_barras)

            st.space("small")

            with st.container(border=True):
                st.markdown(f"**{atributo_x} vs {atributo_y}**")
                scatter_comp = alt.Chart(df_comp).mark_circle(size=150).encode(
                    x=alt.X(f'{atributo_x}:Q', scale=alt.Scale(zero=False)),
                    y=alt.Y(f'{atributo_y}:Q', scale=alt.Scale(zero=False)),
                    color=alt.Color('Jogador:N', legend=alt.Legend(title='Jogador')),
                    tooltip=['Jogador', 'Equipe',
                             alt.Tooltip(f'{atributo_x}:Q', format='.2f'),
                             alt.Tooltip(f'{atributo_y}:Q', format='.2f')]
                ).properties(height=220)
                labels = scatter_comp.mark_text(dy=-12, fontSize=11).encode(text='Jogador:N')
                st.altair_chart(scatter_comp + labels)

    # Tabela comparativa
    if selecionados:
        st.space("medium")
        st.subheader("📋 Tabela comparativa")
        df_tabela = df_filtrado[df_filtrado['Jogador'].isin(selecionados)].copy()
        col_config_comp = {
            'Nota_Moneyball': st.column_config.ProgressColumn(
                'Nota Moneyball', min_value=0, max_value=100, format='%.1f'
            ),
        }
        if 'Nota média' in df_tabela.columns:
            col_config_comp['Nota média'] = st.column_config.ProgressColumn(
                'Nota média FM', min_value=0, max_value=20, format='%.1f'
            )
        st.dataframe(df_tabela, column_config=col_config_comp, hide_index=True)

# ==========================================
# ABA 3: OLHEIRO IA
# ==========================================
with tab_scout:
    st.subheader("🤖 Opinião do Olheiro Chefe")
    st.caption("Análise gerada por inteligência artificial com base nos dados Moneyball.")

    CHAVE_API = st.secrets["CHAVE_API_GEMINI"]
    genai.configure(api_key=CHAVE_API)
    modelo_ia = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

    if 'relatorio_ia_salvo' not in st.session_state:
        if st.button(":material/play_arrow: Gerar relatório do olheiro", type="primary"):
            with st.spinner("O Olheiro IA está analisando e redigindo o relatório..."):
                dados_top = df_filtrado.head(10).to_dict('records')
                prompt = f"""
                Você é o Olheiro Chefe de um time de futebol que usa a filosofia Moneyball.
                Aqui estão os melhores candidatos para a posição {posicao_analise}:
                {dados_top}

                Escreva um texto direto e profissional para o treinador.
                Recomende a contratação de 3 jogadores justificando o custo-benefício e analisando os dados
                em relação aos outros candidatos. Ignore a data de contrato.
                Observe que m é mil e M é milhão. 200m € é igual a 200 mil de euros por exemplo.
                Também verifique a diferença entre os preços dos jogadores.
                Compare a quantidade de partidas também, se for muito baixo em relação aos outros os dados podem ser menos confiáveis.
                Faça uma análise breve de cada um e depois uma conclusão final recomendando o melhor alvo.

                Assine o final como Olheiro IA.
                """
                try:
                    resposta = modelo_ia.generate_content(prompt)
                    st.session_state['relatorio_ia_salvo'] = resposta.text
                    st.rerun()
                except Exception:
                    st.session_state['relatorio_ia_salvo'] = "⚠️ O Olheiro IA está analisando muitos relatórios agora (limite de velocidade do Google). Aguarde 1 minuto e clique em Calcular novamente!"
                    st.rerun()
    else:
        with st.container(border=True):
            st.write(st.session_state['relatorio_ia_salvo'])
        if st.button(":material/refresh: Gerar novo relatório"):
            del st.session_state['relatorio_ia_salvo']
            st.rerun()