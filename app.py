import streamlit as st
import pandas as pd
import main  
import google.generativeai as genai
import altair as alt

st.set_page_config(page_title="Scout Moneyball", page_icon="⚽", layout="wide")

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("⚙️ Configurações")

posicao_analise = st.sidebar.selectbox(
    "Qual posição vamos analisar?",
    ['🧤Goleiros']
)

arquivo_upload = st.sidebar.file_uploader("Sua planilha (.xlsm / .xlsx)", type=["xlsx", "xlsm"])
# ==========================================
# ÁREA PRINCIPAL
# ==========================================
st.title(f"🏆 Moneyball - Análise de {posicao_analise}")

if arquivo_upload is not None:
    
    # 1. CARREGA A PLANILHA INTEIRA APENAS UMA VEZ!
    if 'banco_de_dados_completo' not in st.session_state:
        with st.spinner("Carregando toda a base de dados do FM para a memória..."):
            # sheet_name=None faz o Pandas ler TODAS as abas de uma vez
            st.session_state['banco_de_dados_completo'] = pd.read_excel(arquivo_upload, sheet_name=None, engine='openpyxl')
            st.sidebar.success("Base de dados carregada com sucesso!")

    # Recupera o banco completo da memória
    banco_completo = st.session_state['banco_de_dados_completo']
    
    # Inicializa a trava na memória
    if 'ja_calculou' not in st.session_state:
        st.session_state['ja_calculou'] = False

    # Criamos duas colunas na lateral para os botões ficarem alinhados
    col_btn1, col_btn2 = st.sidebar.columns(2)

    # O parâmetro 'disabled' trava o botão se a variável for True
    if col_btn1.button("🚀 Calcular", disabled=st.session_state['ja_calculou'], use_container_width=True):
        with st.spinner(f"Processando {posicao_analise}..."):
            
            df_aba_selecionada = banco_completo[posicao_analise]
            tabela_processada = main.gerar_ranking(df_aba_selecionada)
            st.session_state['dados_salvos'] = tabela_processada
            
            # Limpa o texto antigo da IA
            if 'relatorio_ia_salvo' in st.session_state:
                del st.session_state['relatorio_ia_salvo']
            
            # Aciona a trava e recarrega a página na mesma hora!
            st.session_state['ja_calculou'] = True
            st.rerun()

    # O botão Recomeçar só aparece se a trava estiver ativada
    if st.session_state['ja_calculou']:
        if col_btn2.button("🔄 Recomeçar", use_container_width=True):
            # Destrava o botão de calcular
            st.session_state['ja_calculou'] = False
            
            # Apaga os dados salvos para limpar a tela
            if 'dados_salvos' in st.session_state:
                del st.session_state['dados_salvos']
            if 'relatorio_ia_salvo' in st.session_state:
                del st.session_state['relatorio_ia_salvo']
                
            # Recarrega a página para voltar ao estado inicial
            st.rerun()    
                            
    # 2. SE A MEMÓRIA ESTIVER CHEIA, mostramos os filtros e a tela!
    # (Isso fica FORA do botão, então não some quando mexemos na barrinha)
    if 'dados_salvos' in st.session_state:
        
        df_resultado = st.session_state['dados_salvos']
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Filtros de Busca")
        
        # O usuário agora pode digitar "20000" diretamente
        valor_maximo_base = float(df_resultado['Valor estimado'].max())
        
        orcamento_max = st.sidebar.number_input(
            "Orçamento Máximo (€)", 
            min_value=0.0, 
            max_value=valor_maximo_base, 
            value=valor_maximo_base, 
            step=5000.0, # Pula de 5 em 5 mil nos botões
            format="%.0f" # Mostra o número sem casas decimais
        )
        
        idade_max = st.sidebar.number_input(
            "Idade Máxima", 
            min_value=15, 
            max_value=45, 
            value=40,
            step=1
        )
        
        # Filtra os dados da memória
        df_filtrado = df_resultado[
            (df_resultado['Valor estimado'] <= orcamento_max) & 
            (df_resultado['Idade'] <= idade_max)
        ]
        
        # ==========================================
        # VISUALIZAÇÃO DA TELA (Gráfico em cima, Tabela embaixo)
        # ==========================================
        if df_filtrado.empty:
            st.warning("Nenhum jogador encontrado com esses filtros. Aumente o orçamento ou a idade!")
        else:
            st.markdown("---")
            st.subheader("🥇 Principal Alvo")
            
            col1, col2, col3 = st.columns(3)
            alvo_ouro = df_filtrado.iloc[0] 
            
            col1.metric(label="Melhor Contratação", value=alvo_ouro['Jogador'], delta=f"Nota: {alvo_ouro['Nota_Moneyball']:.1f}/100")
            col2.metric(label="Valor Estimado", value=f"€ {alvo_ouro['Valor estimado']/1_000_000:.1f}M")
            col3.metric(label="Idade", value=f"{int(alvo_ouro['Idade'])} anos")
            
            st.markdown("---")
            
            df_da_posicao = banco_completo[posicao_analise].copy() # Faz uma cópia para não bagunçar o original
            colunas_para_juntar = ['Jogador', 'Equipe',
                            'Valor estimado', 
                            'Idade', 
                            'Salário', 
                            'Altura', 
                            'Data final de contrato',
                            'Jogos completos',
                            'Expected Goals Prevented xGP',
                            'Falhas/90',
                            '% Acerto do goleiro',
                            'Defesas totais / Jogo',
                            'Nota média']
            df_resultados = df_da_posicao[colunas_para_juntar].copy()
            df_resultados['Nota_Moneyball'] = df_resultado['Nota_Moneyball']
            df_resultados['Equipe'] = df_da_posicao['Equipe']
            df_resultados = df_resultados.sort_values(by='Nota_Moneyball', ascending=False)
            
                     
        # ==========================================
        # LISTA TOP 10 (TEXTO)
        # ==========================================
        col_lista, col_grafico = st.columns([1, 2]) # O gráfico fica mais largo que a lista

        
        with col_lista:
            st.subheader("🏆 Top 10 Recomendados")
            
            # Pega apenas os 10 primeiros
            top_10_lista = df_filtrado.head(10)
            
            # Loop para escrever linha por linha formatado
            # Usamos enumerate(..., 1) para contar de 1 a 10
            for i, row in enumerate(top_10_lista.itertuples(), 1):
                nome = row.Jogador
                
                # st.markdown permite usar **negrito** e organizar bonitinho
                st.markdown(f"**{i}º {nome}**")
                st.write("") # Espaço em branco para separar

       # ==========================================
        # GRÁFICO NATIVO (BONITO E TRAVADO)
        # ==========================================
        with col_grafico:
            st.subheader("📊 Comparativo Detalhado")
            
            # Filtra colunas numéricas e cria o Selectbox
            colunas_numericas = df_resultados.select_dtypes(include=['float64', 'int64']).columns.tolist()
            index_padrao = colunas_numericas.index('Nota_Moneyball') if 'Nota_Moneyball' in colunas_numericas else 0
            
            atributo_escolhido = st.selectbox(
                "Escolha o atributo para comparar o Top 10:", 
                colunas_numericas, 
                index=index_padrao
            )
            
            # Pega os 10 primeiros
            dados_grafico = df_resultados.head(10)
            
            # Cria o gráfico usando Altair
            grafico_bonito = alt.Chart(dados_grafico).mark_bar(
                color='#1f77b4', 
                cornerRadiusEnd=4
                # REMOVI O HEIGHT DAQUI! (Para as barras ficarem com espessura normal)
            ).encode(
                x=alt.X(f'{atributo_escolhido}:Q', title=atributo_escolhido),
                y=alt.Y('Jogador:N', sort='-x', title='', axis=alt.Axis(labelLimit=200)),
                tooltip=['Jogador', alt.Tooltip(f'{atributo_escolhido}:Q', format='.2f')] 
            ).properties(
                height=400 # O tamanho total do gráfico vai aqui!
            )
            
            # Exibe o gráfico travado no Streamlit
            st.altair_chart(grafico_bonito, use_container_width=True)           
            
        st.markdown("---")
        
        st.subheader("📋 Relatório Filtrado")
        st.dataframe(df_resultados.head(10), use_container_width=True, hide_index=True)
            
        st.markdown("---")
        st.subheader("🤖 Opinião do Olheiro Chefe")

        # Pega a chave da API de forma segura escondida no Streamlit
        # NUNCA coloque a chave solta no código que vai pro GitHub Público!
        CHAVE_API = st.secrets["CHAVE_API_GEMINI"]
        genai.configure(api_key=CHAVE_API)
        modelo_ia = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

        if 'relatorio_ia_salvo' not in st.session_state:
            with st.spinner("O Olheiro IA está analisando e redigindo o relatório..."):
                # Prepara os dados
                # 1. Pega os 3 melhores jogadores e converte para texto
                dados_top3 = df_resultados.head(10).to_dict('records')
                    
                # 2. Cria o comando para a IA
                prompt = f"""
                Você é o Olheiro Chefe de um time de futebol que usa a filosofia Moneyball.
                Aqui estão os 3 melhores candidatos encontrados pelo nosso algoritmo matemático:
                {dados_top3}
                    
                Escreva um texto direto e profissional para o treinador. 
                Recomende a contratação de 3 jogadores justificando o custo-benefício e analisando os dados 
                em relação aos outros dois candidatos. Considere que é mais dificil contratar jogadores com contrato longo.
                Também verifique a diferença entre os preços dos jogadores.
                Faça uma análise breve de cada um e depois uma conclusão final recomendando o melhor alvo.
                    
                Assine o final como Olheiro IA.
                """
                
                try:
                    # Tenta chamar o Google
                    resposta = modelo_ia.generate_content(prompt)
                    st.session_state['relatorio_ia_salvo'] = resposta.text
                    st.rerun()
                except Exception as e:
                    # Se o Google der erro de limite de velocidade, salva essa mensagem amigável!
                    mensagem_erro = "⚠️ O Olheiro IA está analisando muitos relatórios agora (limite de velocidade do Google). Aguarde 1 minuto e clique em Calcular novamente!"
                    st.session_state['relatorio_ia_salvo'] = mensagem_erro
                    st.rerun()
        else:
            st.write(st.session_state['relatorio_ia_salvo'])
            
else:
    st.info("👈 Comece fazendo o upload da sua planilha na barra lateral!")