import streamlit as st
import main  

st.set_page_config(page_title="Scout Moneyball", page_icon="⚽", layout="wide")

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("⚙️ Configurações")

posicao_analise = st.sidebar.selectbox(
    "Qual posição vamos analisar?",
    ['🧤Goleiros', 
     #'🧱Zagueiros', 
     #'🛡️Laterais', 
     #'🛡️Volantes', 
     #'⚙️Box-To-Box', 
     #'⚙️Armadores', 
     #'🎯Avançados'
     ]
)

arquivo_upload = st.sidebar.file_uploader("Sua planilha (.xlsm / .xlsx)", type=["xlsx", "xlsm"])

# ==========================================
# ÁREA PRINCIPAL
# ==========================================
st.title(f"🏆 Moneyball - Análise de {posicao_analise}")

if arquivo_upload is not None:
    
    # 1. O botão apenas faz o cálculo pesado e SALVA NA MEMÓRIA
    if st.sidebar.button("🚀 Calcular Ranking"):
        with st.spinner(f"Processando a matemática de {posicao_analise}..."):
            
            # Executa a sua função do main.py
            tabela_processada = main.gerar_ranking(arquivo_upload, posicao_analise)
            
            # Salva o resultado na memória do Streamlit chamada 'dados_salvos'
            st.session_state['dados_salvos'] = tabela_processada
            
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
            
            st.subheader("📊 Comparativo do Top 10")
            dados_grafico = df_filtrado.head(10).set_index('Jogador')[['Nota_Moneyball']]
            st.bar_chart(dados_grafico)
            
            st.markdown("---") 
            
            st.subheader("📋 Relatório Filtrado")
            st.dataframe(df_filtrado.head(15), use_container_width=True, hide_index=True)
            
else:
    st.info("👈 Comece fazendo o upload da sua planilha na barra lateral!")