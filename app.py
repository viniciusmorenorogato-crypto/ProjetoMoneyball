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
# ANIMAÇÃO CSS
# ==========================================
st.markdown("""
<style>
div[data-testid="stTabsContent"] > div {
    animation: fadeSlideIn 0.35s ease;
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0);    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTES
# ==========================================
POSICOES = ['🧤Goleiros', '🧱Zagueiros', '🛡️Laterais', '🛡️Volantes',
            '🏃‍♂️Box-To-Box', '🎯Armadores', '⚽Avançados']

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

COLUNAS_INFO = {'Jogador', 'Equipe', 'Altura', 'Data final de contrato',
                'Data Final de Contrato', 'Data Final do contrato',
                'Fim de contrato', 'Salário', 'Valor estimado', 'Valor Estimado', 'Valor'}

CUSTO = {'Idade', 'Falhas/90', 'Erros Defensivos /90', 'Cartões por falta cometida',
         'Impedimentos / 90', 'Minutos pra MARCAR um gol',
         'Minutos pra acertar uma finalização no gol',
         'Minutos pra PARTICIPAR de um gol',
         'Minutos pra criar uma chance de perigo'}

COLUNAS_ABSOLUTAS_CANDIDATAS = [
    'Jogos completos', 'Jogos Completos', 'Partidas',
    'Gols', 'Assistências', 'Nota média', 'Altura', 'Nacionalidade', 'Pé preferido',
    'Data final de contrato', 'Data Final de Contrato',
    'Data Final do contrato', 'Fim de contrato', 'Contrato', 'Clube',
]

# ==========================================
# SESSION STATE
# ==========================================
if 'ja_calculou' not in st.session_state:
    st.session_state['ja_calculou'] = False
if 'rankings' not in st.session_state:
    st.session_state['rankings'] = {}  # {posicao: df_resultado}

# ==========================================
# CSS GLOBAL
# ==========================================
st.markdown("""
<style>
/* Sidebar: "Feito por" fixo no rodapé */
[data-testid="stSidebar"] > div:first-child {
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    overflow: hidden !important;
}
[data-testid="stSidebarContent"] {
    display: flex;
    flex-direction: column;
    height: 100%;
    overflow-y: auto;
}
.sidebar-footer {
    position: sticky;
    bottom: 0;
    background: #080E0A;
    padding: 10px 0 6px 0;
    text-align: center;
    color: #6B7280;
    font-size: 11px;
    border-top: 1px solid #1E3A24;
    flex-shrink: 0;
}
.sidebar-footer strong { color: #9CA3AF; }

/* Navegação: botões nativos da sidebar estilizados como pills */
[data-testid="stSidebar"] .nav-section div[data-testid="stButton"] > button {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 9px 14px;
    border-radius: 10px;
    border: 1px solid transparent;
    background: transparent;
    color: #9CA3AF;
    font-size: 0.87rem;
    font-weight: 500;
    text-align: left;
    margin-bottom: 3px;
    transition: background 0.18s, border-color 0.18s, color 0.18s,
                transform 0.18s, box-shadow 0.18s;
    position: relative;
}
[data-testid="stSidebar"] .nav-section div[data-testid="stButton"] > button:hover {
    background: #0D1A0F;
    border-color: #1E3A24;
    color: #D1FAE5;
    transform: translateX(4px);
    box-shadow: 0 2px 12px rgba(34,197,94,0.07);
}
[data-testid="stSidebar"] .nav-section div[data-testid="stButton"] > button[kind="primary"] {
    background: #052E0A;
    border-color: #22C55E;
    color: #22C55E;
    font-weight: 700;
    box-shadow: 0 2px 14px rgba(34,197,94,0.13);
}
[data-testid="stSidebar"] .nav-section div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateX(4px);
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("⚙️ Configurações")

arquivo_upload = st.sidebar.file_uploader(
    "Planilha Moneyball (.xlsx ou .xlsm)",
    type=["xlsx", "xlsm"],
    disabled=st.session_state['ja_calculou']
)

st.sidebar.markdown("**🔍 Filtros de jogadores**")
ocultar_nao_a_venda = st.sidebar.checkbox(
    "Ocultar jogadores não à venda",
    value=False,
    disabled=st.session_state['ja_calculou'],
    help="Remove jogadores com valor marcado como 'Não está à venda' ou equivalente."
)
ocultar_valor_desconhecido = st.sidebar.checkbox(
    "Ocultar jogadores com valor desconhecido",
    value=False,
    disabled=st.session_state['ja_calculou'],
    help="Remove jogadores cujo valor de mercado não foi informado."
)

# Navegação por seção — botões animados via session_state
SECOES_LISTA = [
    ("📊", "Dashboard", "dashboard"),
    ("📈", "Comparativo", "comparativo"),
    ("🤖", "Olheiro IA", "scout"),
    ("🔍", "Ficha do Jogador", "ficha"),
    ("📋", "Planilha", "planilha"),
]

if st.session_state['ja_calculou']:
    if 'secao_ativa' not in st.session_state:
        st.session_state['secao_ativa'] = "dashboard"

    st.sidebar.markdown("**📂 Seção**")
    st.sidebar.markdown('<div class="nav-section">', unsafe_allow_html=True)
    for icone, label, chave in SECOES_LISTA:
        ativo = st.session_state['secao_ativa'] == chave
        if st.sidebar.button(
            f"{icone}  {label}",
            key=f"nav_{chave}",
            use_container_width=True,
            type="primary" if ativo else "secondary"
        ):
            st.session_state['secao_ativa'] = chave
            st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    secao_ativa = st.session_state['secao_ativa']
else:
    secao_ativa = "dashboard"

col_btn1, col_btn2 = st.sidebar.columns(2)

if arquivo_upload is not None and not st.session_state['ja_calculou']:
    if col_btn1.button("🚀 Calcular", use_container_width=True):
        with st.spinner("Processando todas as posições..."):
            banco = pd.read_excel(arquivo_upload, sheet_name=None, engine='openpyxl')
            st.session_state['banco_de_dados_completo'] = banco
            rankings = {}
            for pos in POSICOES:
                if pos in banco:
                    try:
                        resultado = main.gerar_ranking(banco[pos], pos)
                        rankings[pos] = resultado
                    except Exception:
                        pass
            st.session_state['rankings'] = rankings
            st.session_state['ja_calculou'] = True
            st.rerun()

if st.session_state['ja_calculou']:
    if col_btn2.button("🔄 Recomeçar", use_container_width=True):
        for key in ['ja_calculou', 'rankings', 'banco_de_dados_completo', 'secao_ativa']:
            if key in st.session_state:
                del st.session_state[key]
        for pos in POSICOES:
            k = f'relatorio_ia_{pos}'
            if k in st.session_state:
                del st.session_state[k]
        st.session_state['ja_calculou'] = False
        st.rerun()

st.sidebar.markdown(
    "<div class='sidebar-footer'>Feito por <strong>Vinícius Rogato</strong></div>",
    unsafe_allow_html=True
)

# ==========================================
# TELA DE BOAS-VINDAS
# ==========================================
if not st.session_state['ja_calculou']:

    st.markdown("""
    <style>
    /* Hero */
    .hero-title { font-size:2.6rem; font-weight:800; letter-spacing:-0.5px; margin-bottom:0; }
    .hero-sub   { font-size:1rem; color:#6B7280; margin-top:4px; margin-bottom:0; }

    /* Steps grid */
    .steps-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; margin:0; }
    .step-card {
        background:#080E0A;
        border:1px solid #1E3A24;
        border-radius:10px;
        padding:14px 12px;
        transition: border-color 0.2s, transform 0.2s;
        cursor:default;
    }
    .step-card:hover { border-color:#22C55E; transform:translateY(-3px); }
    .step-n { font-size:1.4rem; font-weight:800; color:#22C55E; margin-bottom:6px; }
    .step-t { font-size:0.82rem; font-weight:700; color:#E8F5E9; margin-bottom:4px; }
    .step-d { font-size:0.75rem; color:#6B7280; line-height:1.4; }

    /* Channel cards */
    .partners-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
    .partner-card {
        background:#080E0A;
        border:1px solid #1E3A24;
        border-radius:12px;
        padding:16px;
        text-decoration:none;
        display:flex;
        flex-direction:column;
        align-items:center;
        gap:10px;
        transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
        text-align:center;
    }
    .partner-card:hover {
        border-color:#22C55E;
        transform:translateY(-4px);
        box-shadow:0 8px 24px rgba(34,197,94,0.12);
        text-decoration:none;
    }
    .yt-logo { width:36px; height:36px; }
    .partner-name { font-weight:700; font-size:0.92rem; color:#E8F5E9; }
    .partner-handle { font-size:0.75rem; color:#6B7280; }
    .yt-badge {
        display:inline-flex; align-items:center; gap:5px;
        background:#FF0000; color:#fff;
        border-radius:5px; padding:2px 8px;
        font-size:0.7rem; font-weight:700; margin-top:2px;
    }
    .twitch-badge {
        display:inline-flex; align-items:center; gap:5px;
        background:#9146FF; color:#fff;
        border-radius:5px; padding:2px 8px;
        font-size:0.7rem; font-weight:700; margin-top:2px;
    }

    /* Update */
    .update-tag {
        display:inline-block; background:#052E0A; color:#22C55E;
        border:1px solid #1E3A24; border-radius:6px;
        padding:2px 10px; font-size:0.75rem; font-weight:600; margin-bottom:6px;
    }
    .update-item { font-size:0.82rem; color:#9CA3AF; padding:3px 0; }
    </style>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown('<p class="hero-title">🏆 Scout Moneyball</p>', unsafe_allow_html=True)
    st.markdown('<p class="hero-sub">Análise estatística de jogadores do Football Manager com método AHP</p>', unsafe_allow_html=True)

    if arquivo_upload is not None:
        st.success("✅ Planilha carregada! Clique em **🚀 Calcular** na barra lateral para processar todas as posições.")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        # ---- Tutorial compacto em grid ----
        st.markdown("### 📖 Como usar")
        st.space("small")
        st.markdown("""
        <div class="steps-grid">
          <div class="step-card">
            <div class="step-n">1</div>
            <div class="step-t">Upload</div>
            <div class="step-d">Arraste sua planilha .xlsx ou .xlsm na barra lateral</div>
          </div>
          <div class="step-card">
            <div class="step-n">2</div>
            <div class="step-t">Filtros</div>
            <div class="step-d">Oculte jogadores não à venda ou com valor desconhecido</div>
          </div>
          <div class="step-card">
            <div class="step-n">3</div>
            <div class="step-t">Calcular</div>
            <div class="step-d">Clique em 🚀 Calcular — todas as posições são processadas de uma vez</div>
          </div>
          <div class="step-card">
            <div class="step-n">4</div>
            <div class="step-t">Posições</div>
            <div class="step-d">Navegue pelas abas no topo: Goleiros, Zagueiros, Laterais…</div>
          </div>
          <div class="step-card">
            <div class="step-n">5</div>
            <div class="step-t">Seções</div>
            <div class="step-d">Use o menu lateral para Dashboard, Comparativo, IA e Ficha</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.space("medium")

        # ---- Última atualização ----
        st.markdown("### 🔄 Última atualização")
        st.space("small")
        novidades = [
            "Abas por posição — todas processadas de uma vez",
            "Navegação por seções na barra lateral com botões animados",
            "Ficha do jogador com estatísticas completas e comparativo vs líder",
            "Filtros de disponibilidade (à venda / valor desconhecido)",
            "Comparativo interativo com scatter e ranking por atributo",
            "Olheiro IA individual por posição",
            "Tela inicial com tutorial, parceiros e changelog",
        ]
        st.markdown('<span class="update-tag">v2.1 · Jun 2025</span>', unsafe_allow_html=True)
        for n in novidades:
            st.markdown(f'<div class="update-item">• {n}</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown("### 📺 Canais recomendados")
        st.space("small")

        yt_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="#FF0000"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>'
        twitch_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22" height="22" fill="#9146FF"><path d="M11.571 4.714h1.715v5.143H11.57zm4.715 0H18v5.143h-1.714zM6 0L1.714 4.286v15.428h5.143V24l4.286-4.286h3.428L22.286 12V0zm14.571 11.143l-3.428 3.428h-3.429l-3 3v-3H6.857V1.714h13.714z"/></svg>'

        st.markdown(f"""
        <style>
        .ch-row {{ display:flex; gap:8px; margin-bottom:12px; }}
        .ch-card {{
            flex:1; background:#080E0A; border:1px solid #1E3A24;
            border-radius:10px; padding:10px 8px; text-decoration:none !important;
            display:flex; flex-direction:column; align-items:center; gap:4px;
            text-align:center; transition: border-color .2s, transform .2s, box-shadow .2s;
        }}
        .ch-card:hover {{
            border-color:#22C55E; transform:translateY(-4px);
            box-shadow:0 8px 22px rgba(34,197,94,0.13); text-decoration:none !important;
        }}
        .ch-name {{ font-weight:700; font-size:0.8rem; color:#E8F5E9; }}
        .ch-handle {{ font-size:0.66rem; color:#6B7280; }}
        .ch-badge-yt {{
            display:inline-flex; align-items:center; gap:3px;
            background:#FF0000; color:#fff; border-radius:4px;
            padding:1px 5px; font-size:0.6rem; font-weight:700;
        }}
        .ch-badge-tw {{
            display:inline-flex; align-items:center; gap:3px;
            background:#9146FF; color:#fff; border-radius:4px;
            padding:1px 5px; font-size:0.6rem; font-weight:700;
        }}
        .ch-info {{
            background:#080E0A; border:1px solid #1E3A24;
            border-radius:10px; padding:10px 12px; margin-bottom:8px;
        }}
        .ch-info-title {{ font-size:0.77rem; font-weight:700; color:#22C55E; margin-bottom:3px; }}
        .ch-info-desc {{ font-size:0.72rem; color:#9CA3AF; line-height:1.45; }}
        </style>
        <div class="ch-row">
          <a href="https://www.youtube.com/@AllanFCL" target="_blank" class="ch-card">
            {yt_svg}
            <div class="ch-name">Allan FCL</div>
            <div class="ch-handle">@AllanFCL</div>
            <span class="ch-badge-yt">▶ YouTube</span>
          </a>
          <a href="https://www.youtube.com/@Vinteset" target="_blank" class="ch-card">
            {yt_svg}
            <div class="ch-name">Vinteset</div>
            <div class="ch-handle">@Vinteset</div>
            <span class="ch-badge-yt">▶ YouTube</span>
          </a>
          <a href="https://www.twitch.tv/vinteset" target="_blank" class="ch-card">
            {twitch_svg}
            <div class="ch-name">Vinteset</div>
            <div class="ch-handle">vinteset</div>
            <span class="ch-badge-tw">● Twitch</span>
          </a>
        </div>
        <div class="ch-info">
          <div class="ch-info-title">📊 Planilha Moneyball — Allan FCL</div>
          <div class="ch-info-desc">A planilha usada neste app foi desenvolvida em parceria com o Allan FCL.
          Ela estrutura os dados exportados do FM em abas por posição, com métricas específicas para cada
          função tática e compatíveis com o cálculo AHP.</div>
        </div>
        <div class="ch-info">
          <div class="ch-info-title">⌨️ Plugin Ctrl+P — Vinteset</div>
          <div class="ch-info-desc">O plugin <strong style="color:#E8F5E9">Ctrl+P</strong> criado pelo
          Vinteset é essencial para exportar os dados dos jogadores do FM para a planilha. Sem ele, a
          extração de estatísticas não seria possível. Acesse o canal dele para aprender a instalar e usar.</div>
        </div>
        <p style="font-size:0.72rem; color:#6B7280; line-height:1.4; margin-top:4px;">
          🙏 Agradecimento especial ao <strong style="color:#9CA3AF">Allan FCL</strong> e ao
          <strong style="color:#9CA3AF">Vinteset</strong> — acompanhe os canais para aprender mais
          sobre FM26 e montar elencos competitivos!
        </p>
        """, unsafe_allow_html=True)

    st.stop()

# ==========================================
# DADOS CARREGADOS
# ==========================================
banco_completo = st.session_state['banco_de_dados_completo']
rankings = st.session_state['rankings']

# ==========================================
# HELPER: monta df_filtrado para uma posição
# ==========================================
def montar_df(posicao):
    if posicao not in rankings or posicao not in banco_completo:
        return None, None
    df_resultado = rankings[posicao].copy()
    df_da_posicao = banco_completo[posicao].copy()

    colunas_candidatas = COLUNAS_POR_POSICAO.get(posicao, ['Jogador', 'Equipe', 'Idade', 'Nota média'])
    colunas_existentes = [c for c in colunas_candidatas if c in df_da_posicao.columns]

    df_res = df_da_posicao[colunas_existentes].copy().reset_index(drop=True)
    df_notas = df_resultado[["Jogador", "Nota_Moneyball"]].reset_index(drop=True)
    df_res = df_res.merge(df_notas, on="Jogador", how="inner")
    df_res = df_res.sort_values(by="Nota_Moneyball", ascending=False).reset_index(drop=True)
    df_filtrado = df_res.copy()

    # Filtros de disponibilidade
    if ocultar_nao_a_venda or ocultar_valor_desconhecido:
        val_col_filtro = next((c for c in ['Valor estimado', 'Valor Estimado', 'Valor']
                               if c in df_da_posicao.columns), None)
        if val_col_filtro:
            lookup_valor = (
                df_da_posicao[['Jogador', val_col_filtro]]
                .drop_duplicates(subset='Jogador', keep='first')
                .set_index('Jogador')[val_col_filtro]
            )
            val_str = df_filtrado['Jogador'].map(lookup_valor).astype(str).str.strip().str.lower()
            if ocultar_nao_a_venda:
                mask = val_str.isin(['não está à venda', 'nao esta a venda', 'not for sale',
                                     'n/d', 'indisponível', '-', 'nan', ''])
                df_filtrado = df_filtrado[~mask]
            if ocultar_valor_desconhecido:
                mask = val_str.isin(['desconhecido', 'unknown', 'n/a', 'nan', '', '-'])
                df_filtrado = df_filtrado[~mask]
            df_filtrado = df_filtrado.reset_index(drop=True)

    return df_filtrado, df_da_posicao

# ==========================================
# HELPER: renderiza seção de uma posição
# ==========================================
def render_secao(posicao, df_filtrado, df_da_posicao, secao):
    if df_filtrado is None or df_filtrado.empty:
        st.warning(f"Sem dados disponíveis para {posicao}.")
        return

    alvo = df_filtrado.iloc[0]
    colunas_numericas = df_filtrado.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # ------------------------------------------
    if secao == "dashboard":
        st.subheader("🥇 Principal alvo")
        with st.container(horizontal=True):
            st.metric("Melhor contratação", alvo['Jogador'],
                      delta=f"Nota: {alvo['Nota_Moneyball']:.1f}/100", border=True)
            val_col = next((c for c in ['Valor estimado', 'Valor Estimado', 'Valor']
                            if c in alvo.index), None)
            if val_col:
                val = alvo[val_col]
                if isinstance(val, (int, float)) and not math.isnan(val):
                    st.metric("Valor estimado", f"€ {val/1_000_000:.1f}M", border=True)
            st.metric("Idade", f"{int(alvo['Idade'])} anos", border=True)
            sal_col = 'Salário' if 'Salário' in alvo.index else None
            if sal_col:
                sal = alvo[sal_col]
                if isinstance(sal, (int, float)) and not math.isnan(sal):
                    st.metric("Salário", f"€ {sal/1_000:.0f}k/mês", border=True)

        st.space("medium")
        st.subheader("🏆 Top 10 recomendados")
        col_lista, col_dist = st.columns([1, 2], gap="medium")

        with col_lista:
            with st.container(border=True, height=400):
                for i, row in enumerate(df_filtrado.head(10).itertuples(), 1):
                    medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}º")
                    cols_row = st.columns([1, 3, 2])
                    cols_row[0].markdown(medalha)
                    cols_row[1].markdown(f"**{row.Jogador}**")
                    cols_row[2].caption(f"{row.Nota_Moneyball:.1f} pts")

        with col_dist:
            with st.container(border=True, height=400):
                atrib_grafico = st.selectbox(
                    "Dado a exibir:",
                    colunas_numericas,
                    index=colunas_numericas.index("Nota_Moneyball") if "Nota_Moneyball" in colunas_numericas else 0,
                    key=f"dash_atrib_{posicao}"
                )
                chart_dist = alt.Chart(df_filtrado.head(10)).mark_bar(
                    color='#22C55E', cornerRadiusEnd=3
                ).encode(
                    x=alt.X(f'{atrib_grafico}:Q', title=atrib_grafico),
                    y=alt.Y('Jogador:N', sort='-x', title=''),
                    tooltip=['Jogador', 'Equipe',
                             alt.Tooltip(f'{atrib_grafico}:Q', title=atrib_grafico, format='.2f')]
                ).properties(height=310)
                st.altair_chart(chart_dist)

        st.space("medium")
        st.subheader("📊 Nota Moneyball vs Nota média FM")
        with st.container(border=True):
            if 'Nota média' in df_filtrado.columns:
                scatter = alt.Chart(df_filtrado.head(10)).mark_circle(size=90, opacity=0.8).encode(
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



    # ------------------------------------------
    elif secao == "comparativo":
        jogadores_disponiveis = df_filtrado['Jogador'].tolist()
        col_ctrl, col_charts = st.columns([1, 2], gap="medium")

        with col_ctrl:
            with st.container(border=True):
                st.markdown("**Selecione jogadores**")
                selecionados = st.multiselect(
                    "Até 5 jogadores:",
                    options=jogadores_disponiveis,
                    default=jogadores_disponiveis[:3],
                    max_selections=5,
                    placeholder="Digite o nome do jogador...",
                    key=f"comp_sel_{posicao}"
                )
                atributo_barra = st.selectbox(
                    "Atributo para comparar:",
                    colunas_numericas,
                    index=colunas_numericas.index('Nota_Moneyball') if 'Nota_Moneyball' in colunas_numericas else 0,
                    key=f"atrib_barra_{posicao}"
                )
                atributo_x = st.selectbox(
                    "Scatter — Eixo X:",
                    colunas_numericas,
                    index=colunas_numericas.index('Nota_Moneyball') if 'Nota_Moneyball' in colunas_numericas else 0,
                    key=f"eixo_x_{posicao}"
                )
                atributo_y = st.selectbox(
                    "Scatter — Eixo Y:",
                    colunas_numericas,
                    index=min(1, len(colunas_numericas) - 1),
                    key=f"eixo_y_{posicao}"
                )

        with col_charts:
            if selecionados:
                df_comp = df_filtrado[df_filtrado['Jogador'].isin(selecionados)].copy()
                df_comp_sorted = df_comp.sort_values(by=atributo_barra, ascending=False).reset_index(drop=True)
                val_max = df_comp_sorted[atributo_barra].max()
                val_min = df_comp_sorted[atributo_barra].min()
                with st.container(border=True):
                    st.markdown(f"**🏆 Ranking: {atributo_barra}**")
                    for i, row in df_comp_sorted.iterrows():
                        pos = i + 1
                        medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, f"{pos}º")
                        val = row[atributo_barra]
                        pct = ((val - val_min) / (val_max - val_min) * 100) if val_max != val_min else 100
                        val_fmt = f"{val:.2f}" if isinstance(val, float) else str(int(val))
                        r_cols = st.columns([1, 4, 2, 3])
                        r_cols[0].markdown(medalha)
                        r_cols[1].markdown(f"**{row['Jogador']}**")
                        r_cols[2].caption(val_fmt)
                        r_cols[3].progress(int(pct))

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

        if selecionados:
            st.space("medium")
            st.subheader("📋 Tabela comparativa")
            df_tabela = df_filtrado[df_filtrado['Jogador'].isin(selecionados)].copy()
            col_config_comp = {
                'Nota_Moneyball': st.column_config.ProgressColumn(
                    'Nota Moneyball', min_value=0, max_value=100, format='%.1f'),
            }
            if 'Nota média' in df_tabela.columns:
                col_config_comp['Nota média'] = st.column_config.ProgressColumn(
                    'Nota média FM', min_value=0, max_value=20, format='%.1f')
            st.dataframe(df_tabela, column_config=col_config_comp, hide_index=True)

    # ------------------------------------------
    elif secao == "scout":
        st.subheader("🤖 Opinião do Olheiro Chefe")
        st.caption("Análise gerada por inteligência artificial com base nos dados Moneyball.")

        chave_ia = f'relatorio_ia_{posicao}'
        CHAVE_API = st.secrets["CHAVE_API_GEMINI"]
        genai.configure(api_key=CHAVE_API)
        modelo_ia = genai.GenerativeModel('gemini-3.1-flash-lite-preview')

        if chave_ia not in st.session_state:
            if st.button(":material/play_arrow: Gerar relatório do olheiro", type="primary",
                         key=f"btn_ia_{posicao}"):
                with st.spinner("O Olheiro IA está analisando e redigindo o relatório..."):
                    dados_top = df_filtrado.head(10).to_dict('records')
                    prompt = f"""
                    Você é o Olheiro Chefe de um time de futebol que usa a filosofia Moneyball.
                    Aqui estão os melhores candidatos para a posição {posicao}:
                    {dados_top}

                    Escreva um texto direto e profissional para o treinador.
                    Recomende a contratação de 3 jogadores justificando o custo-benefício e analisando os dados
                    em relação aos outros candidatos. Ignore a data de contrato.
                    Observe que m é mil e M é milhão. 200m € é igual a 200 mil de euros por exemplo.
                    Compare a quantidade de partidas — poucos jogos tornam dados menos confiáveis.
                    Faça uma análise breve de cada um e depois uma conclusão final recomendando o melhor alvo.

                    Assine o final como Olheiro IA.
                    """
                    try:
                        resposta = modelo_ia.generate_content(prompt)
                        st.session_state[chave_ia] = resposta.text
                        st.rerun()
                    except Exception:
                        st.session_state[chave_ia] = "⚠️ Limite de velocidade do Google atingido. Aguarde 1 minuto e tente novamente."
                        st.rerun()
        else:
            with st.container(border=True):
                st.write(st.session_state[chave_ia])
            if st.button(":material/refresh: Gerar novo relatório", key=f"btn_ia_refresh_{posicao}"):
                del st.session_state[chave_ia]
                st.rerun()

    # ------------------------------------------
    elif secao == "ficha":
        todos_jogadores = df_filtrado['Jogador'].tolist()
        lider = df_filtrado.iloc[0]

        jogador_sel = st.selectbox(
            "Busque o jogador pelo nome:",
            options=todos_jogadores,
            key=f"ficha_sel_{posicao}",
            placeholder="Digite o nome do jogador..."
        )

        jogador = df_filtrado[df_filtrado['Jogador'] == jogador_sel].iloc[0]
        eh_lider = (jogador_sel == lider['Jogador'])
        rank_pos = todos_jogadores.index(jogador_sel) + 1
        cols_metricas = [c for c in colunas_numericas if c not in COLUNAS_INFO]

        linha_bruta = df_da_posicao[df_da_posicao['Jogador'] == jogador_sel]
        val_col = next((c for c in ['Valor estimado', 'Valor Estimado', 'Valor']
                        if c in df_da_posicao.columns), None)
        sal_col = 'Salário' if 'Salário' in df_da_posicao.columns else None
        nota_jog = jogador['Nota_Moneyball']
        nota_lider = lider['Nota_Moneyball']
        delta_nota = nota_jog - nota_lider if not eh_lider else None
        nota_pct = int(nota_jog)

        # Monta strings de valor e salário
        val_str_fmt = "—"
        if val_col and not linha_bruta.empty:
            v = linha_bruta.iloc[0][val_col]
            try:
                v_num = float(str(v).replace("€","").replace("M","e6").replace("m","e3").replace(",",".").replace(" ",""))
                val_str_fmt = f"€ {v_num/1_000_000:.1f}M"
            except Exception:
                val_str_fmt = str(v)

        sal_str_fmt = "—"
        if sal_col and not linha_bruta.empty:
            s = linha_bruta.iloc[0][sal_col]
            try:
                s_num = float(str(s).replace("€","").replace("m","e3").replace(",",".").replace(" ","").replace("/sem","").replace("p/s",""))
                sal_str_fmt = f"€ {s_num/1_000:.0f}k/sem"
            except Exception:
                sal_str_fmt = str(s)

        # Stat gerais da planilha bruta
        linha_estat = df_da_posicao[df_da_posicao['Jogador'] == jogador_sel]
        colunas_abs = [c for c in COLUNAS_ABSOLUTAS_CANDIDATAS if c in df_da_posicao.columns]
        stats_gerais = {}
        if not linha_estat.empty:
            for c in colunas_abs:
                v = linha_estat.iloc[0][c]
                stats_gerais[c] = "—" if pd.isna(v) else str(v) if not isinstance(v, float) else f"{v:.1f}"

        # CSS da ficha
        rank_badge = {1:"🥇",2:"🥈",3:"🥉"}.get(rank_pos, f"#{rank_pos}")
        delta_color_css = "#22C55E" if (delta_nota is None or delta_nota >= 0) else "#EF4444"
        delta_txt = "Melhor do ranking" if eh_lider else f"{delta_nota:+.1f} vs 1º"

        st.markdown(f"""
        <style>
        .ficha-card {{
            background: #080E0A;
            border: 1px solid #1E3A24;
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 16px;
        }}
        .ficha-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 20px;
        }}
        .ficha-nome {{
            font-size: 1.6rem;
            font-weight: 800;
            color: #E8F5E9;
            line-height: 1.1;
            margin-bottom: 4px;
        }}
        .ficha-equipe {{
            font-size: 0.85rem;
            color: #6B7280;
        }}
        .ficha-nota-circle {{
            min-width: 88px;
            height: 88px;
            border-radius: 50%;
            background: conic-gradient(#22C55E {nota_pct}%, #1E3A24 0%);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        .ficha-nota-inner {{
            width: 68px;
            height: 68px;
            border-radius: 50%;
            background: #080E0A;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .ficha-nota-num {{
            font-size: 1.2rem;
            font-weight: 800;
            color: #22C55E;
            line-height: 1;
        }}
        .ficha-nota-label {{
            font-size: 0.55rem;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .ficha-pills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 14px;
        }}
        .ficha-pill {{
            background: #111A14;
            border: 1px solid #1E3A24;
            border-radius: 8px;
            padding: 6px 12px;
            display: flex;
            flex-direction: column;
            min-width: 90px;
        }}
        .ficha-pill-label {{
            font-size: 0.65rem;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 2px;
        }}
        .ficha-pill-value {{
            font-size: 0.92rem;
            font-weight: 700;
            color: #E8F5E9;
        }}
        .ficha-pill-delta {{
            font-size: 0.68rem;
            font-weight: 600;
            color: {delta_color_css};
        }}
        .ficha-section-title {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #22C55E;
            margin: 18px 0 10px 0;
            padding-bottom: 4px;
            border-bottom: 1px solid #1E3A24;
        }}
        .ficha-metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 8px;
        }}
        .ficha-metric-item {{
            background: #111A14;
            border: 1px solid #1E3A24;
            border-radius: 10px;
            padding: 10px 12px;
        }}
        .ficha-metric-name {{
            font-size: 0.68rem;
            color: #6B7280;
            margin-bottom: 4px;
            line-height: 1.3;
        }}
        .ficha-metric-val {{
            font-size: 1rem;
            font-weight: 700;
            color: #E8F5E9;
        }}
        .ficha-metric-ref {{
            font-size: 0.65rem;
            margin-top: 2px;
        }}
        </style>

        <div class="ficha-card">
          <div class="ficha-header">
            <div>
              <div class="ficha-nome">{jogador['Jogador']}</div>
              <div class="ficha-equipe">{jogador.get('Equipe','—')} · {rank_badge} {rank_pos}º de {len(todos_jogadores)}</div>
              <div class="ficha-pills">
                <div class="ficha-pill">
                  <span class="ficha-pill-label">Idade</span>
                  <span class="ficha-pill-value">{int(jogador['Idade'])} anos</span>
                </div>
                <div class="ficha-pill">
                  <span class="ficha-pill-label">Valor</span>
                  <span class="ficha-pill-value">{val_str_fmt}</span>
                </div>
                <div class="ficha-pill">
                  <span class="ficha-pill-label">Salário</span>
                  <span class="ficha-pill-value">{sal_str_fmt}</span>
                </div>
                {"".join(f'<div class="ficha-pill"><span class="ficha-pill-label">{k}</span><span class="ficha-pill-value">{v}</span></div>' for k,v in stats_gerais.items())}
              </div>
            </div>
            <div class="ficha-nota-circle">
              <div class="ficha-nota-inner">
                <span class="ficha-nota-num">{nota_jog:.0f}</span>
                <span class="ficha-nota-label">/ 100</span>
              </div>
            </div>
          </div>
          <div style="font-size:0.75rem; color:{delta_color_css}; margin-top:10px;">{delta_txt}</div>
        </div>
        """, unsafe_allow_html=True)

        # Métricas vs líder em grid
        st.markdown('<div class="ficha-section-title">Métricas vs melhor do ranking</div>', unsafe_allow_html=True)

        items_html = ""
        for metrica in cols_metricas:
            try:
                val_jog_m = jogador[metrica]
                val_ref_m = lider[metrica]
                if pd.isna(val_jog_m) or pd.isna(val_ref_m):
                    val_display = "—"
                    ref_html = ""
                else:
                    val_display = f"{val_jog_m:.2f}" if isinstance(val_jog_m, float) else str(int(val_jog_m))
                    if not eh_lider:
                        diff = val_jog_m - val_ref_m
                        is_better = (diff < 0) if metrica in CUSTO else (diff > 0)
                        diff_color = "#22C55E" if is_better else ("#EF4444" if diff != 0 else "#6B7280")
                        ref_val = f"{val_ref_m:.2f}" if isinstance(val_ref_m, float) else str(int(val_ref_m))
                        ref_html = f'<div class="ficha-metric-ref" style="color:{diff_color}">{"+" if diff>0 else ""}{diff:.2f} vs {lider["Jogador"][:10]}</div>'
                    else:
                        ref_html = '<div class="ficha-metric-ref" style="color:#22C55E">🥇 Referência</div>'
            except Exception:
                val_display = "—"
                ref_html = ""

            items_html += f"""
            <div class="ficha-metric-item">
              <div class="ficha-metric-name">{metrica}</div>
              <div class="ficha-metric-val">{val_display}</div>
              {ref_html}
            </div>"""

        st.markdown(f'<div class="ficha-metric-grid">{items_html}</div>', unsafe_allow_html=True)

# ==========================================
# ÁREA PRINCIPAL — abas por posição
# ==========================================

# Hero com imagem FM26 como banner + degradê
st.markdown("""
<style>
.fm-hero {
    width: 100%;
    border-radius: 14px;
    overflow: hidden;
    position: relative;
    height: 160px;
    margin-bottom: 20px;
    background:
        linear-gradient(to right,
            #0A0F0D 0%,
            #0A0F0D 15%,
            rgba(10,15,13,0.7) 40%,
            rgba(10,15,13,0) 65%),
        linear-gradient(to top,
            #0A0F0D 0%,
            rgba(10,15,13,0) 40%),
        url("https://raw.githubusercontent.com/viniciusmorenorogato-crypto/ProjetoMoneyball/main/assets/fm26_banner.jpg")
        center/cover no-repeat;
    display: flex;
    align-items: center;
    padding: 0 28px;
}
.fm-hero-text h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 800;
    color: #E8F5E9;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.6);
}
.fm-hero-text p {
    margin: 4px 0 0 0;
    font-size: 0.85rem;
    color: #9CA3AF;
}
</style>
<div class="fm-hero">
  <div class="fm-hero-text">
    <h1>🏆 Scout Moneyball</h1>
    <p>Análise AHP de jogadores do Football Manager</p>
  </div>
</div>
""", unsafe_allow_html=True)

posicoes_disponiveis = [p for p in POSICOES if p in rankings]

if not posicoes_disponiveis:
    st.warning("Nenhuma posição processada com sucesso.")
    st.stop()

abas = st.tabs(posicoes_disponiveis)

for aba, posicao in zip(abas, posicoes_disponiveis):
    with aba:
        df_filtrado, df_da_posicao = montar_df(posicao)

        if secao_ativa == "planilha":
            st.subheader("📋 Planilha completa")
            st.caption("Todos os dados originais da planilha importada.")
            _, df_bruta = montar_df(posicao)
            if df_bruta is not None:
                col_config_pl = {}
                if 'Nota média' in df_bruta.columns:
                    col_config_pl['Nota média'] = st.column_config.ProgressColumn(
                        'Nota média FM', min_value=0, max_value=20, format='%.1f')
                st.dataframe(df_bruta, column_config=col_config_pl, hide_index=True)
        else:
            render_secao(posicao, df_filtrado, df_da_posicao, secao_ativa)