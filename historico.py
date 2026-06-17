"""
historico.py — Gerenciamento de histórico de cálculos Moneyball por usuário.

Cada entrada no histórico contém:
- usuario_id : UUID gerado no browser (persistido via st.query_params)
- criado_em  : timestamp UTC
- hash_dados : SHA-256 dos dados brutos (evita duplicatas consecutivas)
- modo       : 'posicoes' | 'time' | 'overall'
- dados      : dict com top 10 por posição { posicao: [{Jogador, Nota_Moneyball, Equipe}, ...] }

O histórico mantém no máximo 10 entradas por usuário (remove as mais antigas).
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

MAX_HISTORICO = 10
TABELA = "historico_moneyball"

# ── Conexão com Supabase ───────────────────────────────────────────────────
@st.cache_resource
def _get_supabase():
    """Retorna o cliente Supabase, usando as credenciais do secrets.toml."""
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        client = create_client(url, key)
        return client
    except KeyError as e:
        # Chave não encontrada no secrets.toml
        print(f"[Supabase] Chave ausente no secrets: {e}")
        return None
    except Exception as e:
        print(f"[Supabase] Erro ao conectar: {e}")
        return None


def supabase_disponivel() -> bool:
    """Retorna True se o Supabase está configurado e acessível."""
    try:
        # Verifica se as chaves existem antes de tentar conectar
        _ = st.secrets["SUPABASE_URL"]
        _ = st.secrets["SUPABASE_KEY"]
        client = _get_supabase()
        return client is not None
    except Exception:
        return False


def diagnostico_supabase() -> str:
    """Retorna uma string descrevendo o estado da conexão (para debug)."""
    try:
        url = st.secrets.get("SUPABASE_URL", None)
        key = st.secrets.get("SUPABASE_KEY", None)
        if not url:
            return "❌ SUPABASE_URL não encontrada no secrets"
        if not key:
            return "❌ SUPABASE_KEY não encontrada no secrets"
        client = _get_supabase()
        if client is None:
            return "❌ Cliente Supabase retornou None (erro ao conectar)"
        return f"✅ Conectado ({url[:40]}...)"
    except Exception as e:
        return f"❌ Exceção: {e}"


# ── Identificação do usuário ───────────────────────────────────────────────
def obter_ou_criar_usuario_id() -> str:
    """
    Obtém o UUID do usuário salvo em st.query_params.
    Se não existir, gera um novo e salva.
    """
    params = st.query_params
    uid = params.get("uid", None)
    if not uid:
        uid = str(uuid.uuid4())
        st.query_params["uid"] = uid
    return uid


# ── Hash de dados ──────────────────────────────────────────────────────────
def calcular_hash_rankings(rankings: dict) -> str:
    """
    Gera um SHA-256 dos rankings atuais para detectar planilha duplicada.
    Normaliza para garantir ordem consistente.
    """
    dados_str = json.dumps(
        {pos: df.to_dict('records') for pos, df in sorted(rankings.items())},
        ensure_ascii=False,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(dados_str.encode()).hexdigest()


# ── Leitura do histórico ────────────────────────────────────────────────────
def carregar_historico(usuario_id: str) -> list[dict]:
    """
    Retorna a lista de entradas do histórico do usuário, ordenadas da mais
    recente para a mais antiga. Retorna [] em caso de erro.
    """
    client = _get_supabase()
    if not client:
        return []
    try:
        resp = (
            client.table(TABELA)
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("criado_em", desc=True)
            .limit(MAX_HISTORICO)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


# ── Gravação do histórico ───────────────────────────────────────────────────
def salvar_calculo(usuario_id: str, rankings: dict, modo: str) -> tuple[bool, str]:
    """
    Salva um novo cálculo no histórico.

    Regras:
    - Se o hash dos rankings for igual ao da entrada mais recente, não salva (duplicata).
    - Mantém no máximo MAX_HISTORICO entradas; remove as mais antigas se necessário.

    Retorna: (salvo: bool, mensagem: str)
    """
    client = _get_supabase()
    if not client:
        return False, "Supabase não configurado."

    try:
        hash_atual = calcular_hash_rankings(rankings)

        # Verifica duplicata com a entrada mais recente
        historico = carregar_historico(usuario_id)
        if historico and historico[0].get("hash_dados") == hash_atual:
            return False, "Planilha idêntica ao último cálculo — histórico não sobrescrito."

        # Prepara dados: top 10 por posição
        dados_top10 = {}
        for pos, df in rankings.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                cols = [c for c in ["Jogador", "Equipe", "Nota_Moneyball", "Rating_Overall"] if c in df.columns]
                dados_top10[pos] = df[cols].head(10).to_dict("records")

        entrada = {
            "usuario_id": usuario_id,
            "criado_em": datetime.now(timezone.utc).isoformat(),
            "hash_dados": hash_atual,
            "modo": modo,
            "dados": dados_top10,
        }

        client.table(TABELA).insert(entrada).execute()

        # Remove entradas excedentes (mantém apenas as MAX_HISTORICO mais recentes)
        if len(historico) >= MAX_HISTORICO:
            ids_antigos = [h["id"] for h in historico[MAX_HISTORICO - 1:]]
            if ids_antigos:
                client.table(TABELA).delete().in_("id", ids_antigos).execute()

        return True, "Histórico salvo com sucesso."

    except Exception as e:
        return False, f"Erro ao salvar histórico: {e}"


# ── Deleção de entrada ──────────────────────────────────────────────────────
def deletar_entrada(entrada_id: str) -> bool:
    """Remove uma entrada específica do histórico pelo ID."""
    client = _get_supabase()
    if not client:
        return False
    try:
        client.table(TABELA).delete().eq("id", entrada_id).execute()
        return True
    except Exception:
        return False


# ── SQL para criar a tabela (guia de setup) ─────────────────────────────────
SQL_CRIAR_TABELA = """
-- Cole este SQL no Editor do seu projeto Supabase (SQL Editor → New Query)

create table if not exists historico_moneyball (
    id          uuid default gen_random_uuid() primary key,
    usuario_id  text        not null,
    criado_em   timestamptz not null default now(),
    hash_dados  text        not null,
    modo        text        not null default 'posicoes',
    dados       jsonb       not null default '{}'::jsonb
);

-- Índice para busca rápida por usuário
create index if not exists idx_historico_usuario
    on historico_moneyball (usuario_id, criado_em desc);

-- Row Level Security: cada usuário só vê/edita seus próprios dados
alter table historico_moneyball enable row level security;

create policy "usuarios podem ver seu proprio historico"
    on historico_moneyball for select
    using (true);

create policy "usuarios podem inserir seu proprio historico"
    on historico_moneyball for insert
    with check (true);

create policy "usuarios podem deletar seu proprio historico"
    on historico_moneyball for delete
    using (true);
"""


# ══════════════════════════════════════════════════════════════════════════════
# E-MAILS DO OLHEIRO
# ══════════════════════════════════════════════════════════════════════════════

TABELA_EMAILS = "emails_olheiro"
MAX_EMAILS = 10


def salvar_email_olheiro(usuario_id: str, posicao: str, modo: str,
                          perspectiva: str, texto: str) -> tuple[bool, str]:
    """
    Salva um relatório gerado pelo Olheiro IA no histórico de e-mails.

    posicao    : nome da aba (ex: '🧤Goleiros', '📊Time Estatísticas')
    modo       : 'posicoes' | 'time' | 'overall'
    perspectiva: 'proprio' | 'adversario' | '' (para posições/overall)
    texto      : conteúdo completo gerado pela IA

    Mantém no máximo MAX_EMAILS por usuário, removendo os mais antigos.
    Retorna (salvo: bool, mensagem: str)
    """
    client = _get_supabase()
    if not client:
        return False, "Supabase não configurado."

    try:
        entrada = {
            "usuario_id": usuario_id,
            "criado_em":  datetime.now(timezone.utc).isoformat(),
            "posicao":    posicao,
            "modo":       modo,
            "perspectiva": perspectiva,
            "texto":      texto,
        }
        client.table(TABELA_EMAILS).insert(entrada).execute()

        # Remove excedentes
        existentes = (
            client.table(TABELA_EMAILS)
            .select("id")
            .eq("usuario_id", usuario_id)
            .order("criado_em", desc=True)
            .execute()
        )
        ids_todos = [r["id"] for r in (existentes.data or [])]
        if len(ids_todos) > MAX_EMAILS:
            ids_antigos = ids_todos[MAX_EMAILS:]
            client.table(TABELA_EMAILS).delete().in_("id", ids_antigos).execute()

        return True, "E-mail do Olheiro salvo."
    except Exception as e:
        return False, f"Erro ao salvar e-mail: {e}"


def carregar_emails_olheiro(usuario_id: str) -> list[dict]:
    """
    Retorna os e-mails do Olheiro do usuário, do mais recente ao mais antigo.
    """
    client = _get_supabase()
    if not client:
        return []
    try:
        resp = (
            client.table(TABELA_EMAILS)
            .select("*")
            .eq("usuario_id", usuario_id)
            .order("criado_em", desc=True)
            .limit(MAX_EMAILS)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


def deletar_email_olheiro(entrada_id: str) -> bool:
    """Remove um e-mail específico pelo ID."""
    client = _get_supabase()
    if not client:
        return False
    try:
        client.table(TABELA_EMAILS).delete().eq("id", entrada_id).execute()
        return True
    except Exception:
        return False


SQL_CRIAR_TABELA_EMAILS = """
-- Cole no SQL Editor do Supabase junto com a tabela de histórico de ranking

create table if not exists emails_olheiro (
    id          uuid default gen_random_uuid() primary key,
    usuario_id  text        not null,
    criado_em   timestamptz not null default now(),
    posicao     text        not null,
    modo        text        not null default 'posicoes',
    perspectiva text        not null default '',
    texto       text        not null
);

create index if not exists idx_emails_usuario
    on emails_olheiro (usuario_id, criado_em desc);

alter table emails_olheiro enable row level security;

create policy "select emails"  on emails_olheiro for select  using (true);
create policy "insert emails"  on emails_olheiro for insert  with check (true);
create policy "delete emails"  on emails_olheiro for delete  using (true);

-- Limpeza automática dos e-mails também (adicionar ao job pg_cron existente):
-- delete from emails_olheiro where criado_em < now() - interval '7 days';
"""