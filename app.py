import streamlit as st
import pandas as pd
import main  
import google.generativeai as genai
import altair as alt

st.set_page_config(
    page_title="Scout Moneyball",
    page_icon=":material/sports_soccer:",
    layout="wide",
)

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
if 'ja_calculou' not in st.session_state:
    st.session_state['ja_calculou'] = False

st.sidebar.title(":material/tune: Configurações")

posicao_analise = st.sidebar.selectbox(
    "Posição para análise:", 
    ['🧤Goleiros', '🧱Zagueiros', '🛡️Laterais', '🛡️Volantes', '🏃‍♂️Box-To-Box', '🎯Armadores', '⚽Avançados'],
    disabled=st.session_state['ja_calculou'] 
)

arquivo_upload = st.sidebar.file_uploader(
    "Planilha Moneyball (.xlsx ou .xlsm)", 
    type=["xlsx", "xlsm"],
    disabled=st.session_state['ja_calculou'] 
)

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
st.title(f":material/sports_soccer: Moneyball — {posicao_analise}")

if arquivo_upload is None and not st.session_state['ja_calculou']:
    # Tela de boas-vindas
    st.title(":material/sports_soccer: Scout Moneyball")
    with st.container(border=True):
        st.subheader(":material/info: Como usar")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            with st.container(border=True):
                st.markdown(":material/upload_file: **1. Upload**")
                st.caption("Arraste sua planilha Moneyball (.xlsx ou .xlsm) na barra lateral.")
        with col_b:
            with st.container(border=True):
                st.markdown(":material/tune: **2. Configure**")
                st.caption("Selecione a posição que deseja analisar.")
        with col_c:
            with st.container(border=True):
                st.markdown(":material/play_arrow: **3. Calcule**")
                st.caption("Clique em Calcular e explore os rankings e dashboards.")
    st.stop()


if arquivo_upload is not None:
    
    if 'banco_de_dados_completo' not in st.session_state:
        with st.spinner("Carregando base de dados do FM..."):
            st.session_state['banco_de_dados_completo'] = pd.read_excel(
                arquivo_upload, sheet_name=None, engine='openpyxl'
            )
            st.sidebar.success("Base carregada!", icon=":material/check_circle:")

    banco_completo = st.session_state['banco_de_dados_completo']
    
    col_btn1, col_btn2 = st.sidebar.columns(2)

    if col_btn1.button(
        ":material/play_arrow: Calcular",
        disabled=st.session_state['ja_calculou'],
        use_container_width=True
    ):
        with st.spinner(f"Processando {posicao_analise}..."):
            df_aba_selecionada = banco_completo[posicao_analise]
            tabela_processada = main.gerar_ranking(df_aba_selecionada, posicao_analise)
            st.session_state['dados_salvos'] = tabela_processada
            
            if 'relatorio_ia_salvo' in st.session_state:
                del st.session_state['relatorio_ia_salvo']
            
            st.session_state['ja_calculou'] = True
            st.rerun()

    if st.session_state['ja_calculou']:
        if col_btn2.button(":material/refresh: Recomeçar", use_container_width=True):
            st.session_state['ja_calculou'] = False
            if 'dados_salvos' in st.session_state:
                del st.session_state['dados_salvos']
            if 'relatorio_ia_salvo' in st.session_state:
                del st.session_state['relatorio_ia_salvo']
            st.rerun()    
                            
    if 'dados_salvos' in st.session_state:
        
        df_resultado = st.session_state['dados_salvos']
        df_filtrado = df_resultado.copy()

        if df_filtrado.empty:
            st.warning(
                "Nenhum jogador encontrado com esses filtros. Aumente o orçamento ou a idade!",
                icon=":material/warning:"
            )
        else:
            # ==========================================
            # PRINCIPAL ALVO
            # ==========================================
            st.subheader(":material/emoji_events: Principal alvo Moneyball")
            
            alvo_ouro = df_filtrado.iloc[0]
            col1, col2, col3 = st.columns(3)
            
            col1.metric(
                label="Melhor contratação",
                value=alvo_ouro['Jogador'],
                delta=f"Nota: {alvo_ouro['Nota_Moneyball']:.1f}/100"
            )
            col2.metric(
                label="Valor estimado",
                value=f"€ {alvo_ouro['Valor estimado']/1_000_000:.1f}M"
            )
            col3.metric(
                label="Idade",
                value=f"{int(alvo_ouro['Idade'])} anos"
            )
            
            # Monta df_resultados com colunas da posição
            df_da_posicao = banco_completo[posicao_analise].copy()
            if posicao_analise == '🧤Goleiros':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor estimado', 'Idade', 'Salário', 'Altura',
                                'Data final de contrato', 'Jogos completos', 'Expected Goals Prevented xGP',
                                'Falhas/90', '% Acerto do goleiro', 'Defesas totais / Jogo', 'Nota média']
            elif posicao_analise == '🧱Zagueiros':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Altura',
                                'Data final de contrato', 'Jogos completos', 'Desarmes Decisivos / 90',
                                'Acertos (Cabs, Des, Pres)', 'Acertos/90', 'Bolas roubadas /90',
                                '% Bolas disputadas e ganhas', 'Erros Defensivos /90', 'Eficácia defensiva', 'Nota média']
            elif posicao_analise == '🛡️Laterais':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor Estimado', 'Idade', 'Salário', 'Altura',
                                'Jogos completos', 'Participação / 90', 'Fintas / 90',
                                'Minutos pra criar uma chance de perigo', 'Cruzamentos Conseguidos',
                                'xA + xG /90', 'Gols + A/90', 'Movimentos ofensivos com sucesso',
                                'Dist / 90', 'Erros Defensivos /90', 'Eficácia defensiva', 'Nota média']
            elif posicao_analise == '🛡️Volantes':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Jogos Completos',
                                'Data Final de Contrato', 'Cartões por falta cometida',
                                '% Pressão ganha/90', '% Bolas disputadas e ganhas (sem falta)',
                                'Passes certos  - errados / Jogo', 'Passes em progressão/90',
                                'Eficácia defensiva', 'xA por passe decisivo', 'Criação / 90',
                                'Distância /90', 'Nota média']
            elif posicao_analise == '🏃‍♂️Box-To-Box':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Jogos completos',
                                'Fim de contrato', 'Taxa de Conversão %',
                                'Participação por jogo (passes, fnt, fin, criação, roubadas de bola, etc)',
                                '% Acerto', 'xA / Passe Decisivo', 'Dist / 90', 'Último terço/90', 'Nota média']
            elif posicao_analise == '🎯Armadores':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor', 'Idade', 'Salário', 'Jogos completos',
                                'Data Final do contrato', 'Gols+ Assist / 90', 'Fintas /90',
                                'non Pen xG /90', 'xA /90', '% Cruzamentos certos',
                                'Passes Decisivos pra uma assistência', 'xA / Passe Decisivo',
                                'Finalizações no gol/90', 'Conversão dos chutes de fora da  área',
                                'Ações com Bola T/90', '% Sucesso de ações com bola',
                                'Ações que geraram finalizações ao gol /90', 'Chances de perigo criadas /90',
                                'Participação do jogador a cada 90 minutos (fnt, cabs, pass, finalizaçõs)',
                                'Participação em passes / 90', 'Passes em construção de jog OF /90',
                                'Ações no último terço / 90', 'Tentativas de marcar um gol / 90',
                                'Dist / 90', 'Sprints/90', 'Nota média']
            elif posicao_analise == '⚽Avançados':
                colunas_para_juntar = ['Jogador', 'Equipe', 'Valor Estimado', 'Idade', 'Salário', 'Jogos completos',
                                'Data Final do contrato', 'Média de gols em toda a Carreira',
                                'Média gols / partida', 'Média gols + ass / partida',
                                'Gols Sem Pênalti /90', 'Gols de dentro da área /90',
                                'Gols de fora da área /90', '% Cabs ganhos', 'Impedimentos / 90',
                                'Finalizações no gol/90', 'GPI (Goal Probability Index)',
                                'Over xG / Under xG per 90', 'Minutos pra acertar uma finalização no gol',
                                'Minutos pra MARCAR um gol', 'Minutos pra PARTICIPAR de um gol',
                                'Gols não esperados SEM PÊNALTI', 'xG Conclusion', 'Pass D /90',
                                'Fintas/90', '% Des + Pressões concluídas', 'Dist / 90',
                                'Eficácia ofensiva', 'Participação do jogador a cada 90 minutos',
                                '% Sucesso de ações com bola', 'Tentativas de marcar um gol  /90', 'Nota média']
                
            df_resultados = df_da_posicao[colunas_para_juntar].copy()
            df_resultados['Nota_Moneyball'] = df_resultado['Nota_Moneyball']
            df_resultados['Equipe'] = df_da_posicao['Equipe']
            df_resultados = df_resultados.sort_values(by='Nota_Moneyball', ascending=False)
                    
            # ==========================================
            # TOP 10 + GRÁFICO
            # ==========================================
            col_lista, col_grafico = st.columns([1, 2])

            with col_lista:
                st.subheader(":material/leaderboard: Top 10 recomendados")
                top_10_lista = df_filtrado.head(10)
                for i, row in enumerate(top_10_lista.itertuples(), 1):
                    st.markdown(f"**{i}º {row.Jogador}**")
                    st.space("small")

            with col_grafico:
                st.subheader(":material/bar_chart: Comparativo detalhado")
                
                colunas_numericas = df_resultados.select_dtypes(include=['float64', 'int64']).columns.tolist()
                index_padrao = colunas_numericas.index('Nota_Moneyball') if 'Nota_Moneyball' in colunas_numericas else 0
                
                atributo_escolhido = st.selectbox(
                    "Atributo para comparar o top 10:", 
                    colunas_numericas, 
                    index=index_padrao
                )
                
                dados_grafico = df_resultados.head(10)
                
                grafico_bonito = alt.Chart(dados_grafico).mark_bar(
                    color='#22C55E', 
                    cornerRadiusEnd=4
                ).encode(
                    x=alt.X(f'{atributo_escolhido}:Q', title=atributo_escolhido),
                    y=alt.Y('Jogador:N', sort='-x', title='', axis=alt.Axis(labelLimit=200)),
                    tooltip=['Jogador', alt.Tooltip(f'{atributo_escolhido}:Q', format='.2f')] 
                ).properties(height=400)
                
                st.altair_chart(grafico_bonito, use_container_width=True)           
            
            # ==========================================
            # TABELA
            # ==========================================
            st.subheader(":material/table_chart: Relatório filtrado")
            st.dataframe(df_resultados.head(10), use_container_width=True, hide_index=True)
                
            # ==========================================
            # RELATÓRIO IA
            # ==========================================
            st.subheader(":material/smart_toy: Opinião do olheiro chefe")

            CHAVE_API = st.secrets["CHAVE_API_GEMINI"]
            genai.configure(api_key=CHAVE_API)
            modelo_ia = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

            if 'relatorio_ia_salvo' not in st.session_state:
                with st.spinner("O olheiro IA está analisando e redigindo o relatório..."):
                    dados_top3 = df_resultados.head(10).to_dict('records')
                    prompt = f"""
                    Você é o Olheiro Chefe de um time de futebol que usa a filosofia Moneyball.
                    Aqui estão os 3 melhores candidatos encontrados pelo nosso algoritmo matemático:
                    {dados_top3}
                        
                    Escreva um texto direto e profissional para o treinador. 
                    Recomende a contratação de 3 jogadores justificando o custo-benefício e analisando os dados 
                    em relação aos outros dois candidatos. Ignore a data de contrato.
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
                    except Exception as e:
                        mensagem_erro = "⚠️ O Olheiro IA está analisando muitos relatórios agora (limite de velocidade do Google). Aguarde 1 minuto e clique em Calcular novamente!"
                        st.session_state['relatorio_ia_salvo'] = mensagem_erro
                        st.rerun()
            else:
                st.write(st.session_state['relatorio_ia_salvo'])
            
else:
    st.caption("👈 Faça o upload da sua planilha Moneyball na barra lateral para começar.")