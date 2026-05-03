import streamlit as st
import pandas as pd
import main  
import google.generativeai as genai

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
    
    # 2. O BOTÃO AGORA É INSTANTÂNEO
    if st.sidebar.button("🚀 Calcular Ranking"):
        with st.spinner(f"Processando a matemática de {posicao_analise}..."):
            
            # Pega SÓ a aba que o usuário selecionou no menu
            df_aba_selecionada = banco_completo[posicao_analise]
            
            # Passa a aba já lida para o main.py trabalhar
            tabela_processada = main.gerar_ranking(df_aba_selecionada)
            st.session_state['dados_salvos'] = tabela_processada
            st.sidebar.success("Ranking calculado e salvo na memória!")
                            
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
            
                     
            st.subheader("📊 Comparativo do Top 10")
            dados_grafico = df_resultados.head(10).set_index('Jogador')[['Nota_Moneyball']]
            st.bar_chart(dados_grafico)
            
            st.markdown("---") 
            
            st.subheader("📋 Relatório Filtrado")
            st.dataframe(df_resultados.head(10), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("🤖 Relatório do Olheiro Chefe (IA)")

            # Pega a chave da API de forma segura escondida no Streamlit
            # NUNCA coloque a chave solta no código que vai pro GitHub Público!
            CHAVE_API = st.secrets["CHAVE_API_GEMINI"]
            genai.configure(api_key=CHAVE_API)
            modelo_ia = genai.GenerativeModel('gemini-2.5-flash')

            if 'relatorio_ia_salvo' not in st.session_state:
                with st.spinner("O Olheiro IA está redigindo o relatório..."):
                        
                    # 1. Pega os 3 melhores jogadores e converte para texto
                    dados_top3 = df_resultados.head(5).to_dict('records')
                        
                    # 2. Cria o comando para a IA
                    prompt = f"""
                    Você é o Olheiro Chefe de um time de futebol que usa a filosofia Moneyball.
                    Aqui estão os 3 melhores candidatos encontrados pelo nosso algoritmo matemático:
                    {dados_top3}
                        
                    Escreva um parágrafo curto, direto e profissional para o treinador. 
                    Recomende a contratação de 3 jogadores justificando o custo-benefício e analisando os dados 
                    em relação aos outros dois candidatos.
                        
                    Assine o final como Olheiro IA.
                    """
                        
                    # 3. Chama a IA e imprime a resposta na tela web
                    resposta = modelo_ia.generate_content(prompt)
                    st.write(resposta.text)
                    st.session_state['relatorio_ia_salvo'] = resposta.text
            else:
                st.write(st.session_state['relatorio_ia_salvo'])
            
            
else:
    st.info("👈 Comece fazendo o upload da sua planilha na barra lateral!")