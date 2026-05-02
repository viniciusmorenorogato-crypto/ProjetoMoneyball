import streamlit as st
import main  # Importa o seu arquivo principal!

# Configuração da Página Web
st.set_page_config(page_title="Scout Moneyball", page_icon="⚽", layout="wide")

st.title("🏆 Projeto Moneyball - Análise AHP")
st.markdown("Faça o upload da sua planilha do Football Manager para descobrir os melhores alvos!")

# Widget de Upload
arquivo_upload = st.file_uploader("Arraste seu arquivo .xlsm ou .xlsx aqui", type=["xlsx", "xlsm"])

if arquivo_upload is not None:
    st.success("Planilha carregada na memória!")
    
    if st.button("🚀 Calcular Ranking Moneyball"):
        
        with st.spinner("Lendo dados, calculando Matriz AHP e gerando ranking..."):
            
            # CHAMA O SEU CÓDIGO AQUI! Passando o arquivo que o usuário upou
            df_resultado = main.gerar_ranking(arquivo_upload)
            
            st.subheader("🥇 Top 10 Alvos Recomendados")
            
            # Mostra a tabela lindamente na tela web
            st.dataframe(df_resultado.head(10), use_container_width=True)
            
            st.balloons()