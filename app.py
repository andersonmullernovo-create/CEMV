import base64
import datetime
import hashlib
import json
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

try:
  from streamlit_gsheets import GSheetsConnection

  HAS_GSHEETS_LIB = True
except ImportError:
  HAS_GSHEETS_LIB = False

# Configuração da página orientada ao setor alimentício
st.set_page_config(
    page_title="Gestão de Stock - RBM Alimentos",
    page_icon="🍲",
    layout="wide",
)

# --- FICHEIROS DE PERSISTÊNCIA LOCAL (FALLBACK) ---
ARQ_ESTOQUE = "estoque_rbm_dados.csv"
ARQ_SETORES = "setores_rbm_dados.json"
ARQ_USERS = "users_rbm_dados.json"
ARQ_HIST = "historico_rbm_dados.csv"
ARQ_CONFIG = "config_visual_dados.json"
ARQ_MENSAGENS = "mensagens_rbm_dados.json"
ARQ_CLIENTES = "clientes_rbm_dados.json"
ARQ_CLIENTES_PEDIDOS = "clientes_pedidos_dados.json"

TEMAS_FUNDO = {
    "Gradiente Azul Moderno": "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
    "Industrial RBM / Aço Escovado": (
        "linear-gradient(135deg, #2c3e50 0%, #34495e 100%)"
    ),
    "Modo Escuro Sofisticado": (
        "linear-gradient(135deg, #1f1c2c 0%, #928dab 100%)"
    ),
    "Clássico Alimentício / Creme": (
        "linear-gradient(135deg, #fdfbf7 0%, #e8e1d5 100%)"
    ),
    "Verde Armazém Fresco": "linear-gradient(135deg, #ebf5fb 0%, #d4efdf 100%)",
}


# --- SEGURANÇA DE SENHAS (HASH SHA-256) ---
def hash_senha(senha: str) -> str:
  return hashlib.sha256(str(senha).encode("utf-8")).hexdigest()


def verificar_senha(senha_digitada: str, senha_guardada: str) -> bool:
  if not senha_guardada:
    return False
  if len(senha_guardada) == 64 and all(
      c in "0123456789abcdef" for c in senha_guardada.lower()
  ):
    return hash_senha(senha_digitada) == senha_guardada.lower()
  return senha_digitada == senha_guardada


# --- CAMADA DE PERSISTÊNCIA (GOOGLE SHEETS SE CONFIGURADO + DISCO LOCAL) ---
def _gsheets_ativo() -> bool:
  if not HAS_GSHEETS_LIB:
    return False
  try:
    return "connections" in st.secrets and "gsheets" in st.secrets["connections"]
  except Exception:
    return False


def _get_conn():
  return st.connection("gsheets", type=GSheetsConnection)


def ler_json_persistente(aba: str, caminho_local: str, padrao):
  if _gsheets_ativo():
    try:
      conn = _get_conn()
      df_aba = conn.read(worksheet=aba, ttl=0)
      if (
          df_aba is not None
          and not df_aba.empty
          and "payload_json" in df_aba.columns
      ):
        raw = str(df_aba.iloc[0]["payload_json"]).strip()
        if raw and raw != "nan":
          dados = json.loads(raw)
          with open(caminho_local, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)
          return dados
    except Exception:
      pass

  if os.path.exists(caminho_local):
    try:
      with open(caminho_local, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      pass
  return padrao


def salvar_json_persistente(aba: str, caminho_local: str, dados):
  with open(caminho_local, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False)

  if _gsheets_ativo():
    try:
      conn = _get_conn()
      df_payload = pd.DataFrame(
          [{"payload_json": json.dumps(dados, ensure_ascii=False)}]
      )
      conn.update(worksheet=aba, data=df_payload)
    except Exception as e:
      st.toast(f"⚠️ Aviso ao sincronizar '{aba}' na nuvem: {e}")


def ler_df_persistente(
    aba: str, caminho_local: str, padrao_df: pd.DataFrame
) -> pd.DataFrame:
  if _gsheets_ativo():
    try:
      conn = _get_conn()
      df_aba = conn.read(worksheet=aba, ttl=0)
      if df_aba is not None and not df_aba.empty:
        df_aba.to_csv(caminho_local, index=False)
        return df_aba
    except Exception:
      pass

  if os.path.exists(caminho_local):
    try:
      return pd.read_csv(caminho_local)
    except Exception:
      pass
  return padrao_df.copy()


def salvar_df_persistente(aba: str, caminho_local: str, df_alvo: pd.DataFrame):
  df_alvo.to_csv(caminho_local, index=False)
  if _gsheets_ativo():
    try:
      conn = _get_conn()
      conn.update(worksheet=aba, data=df_alvo)
    except Exception as e:
      st.toast(f"⚠️ Aviso ao sincronizar '{aba}' na nuvem: {e}")


def salvar_estoque():
  salvar_df_persistente("estoque", ARQ_ESTOQUE, st.session_state.estoque)


def salvar_setores():
  salvar_json_persistente("setores", ARQ_SETORES, st.session_state.setores)


def salvar_users():
  salvar_json_persistente("users", ARQ_USERS, st.session_state.users)


def salvar_historico():
  salvar_df_persistente("historico", ARQ_HIST, st.session_state.historico)


def salvar_config():
  salvar_json_persistente(
      "config_visual", ARQ_CONFIG, st.session_state.config_visual
  )


def salvar_mensagens():
  salvar_json_persistente(
      "mensagens", ARQ_MENSAGENS, st.session_state.mensagens
  )


def salvar_clientes():
  salvar_json_persistente("clientes", ARQ_CLIENTES, st.session_state.clientes)


def salvar_clientes_pedidos():
  salvar_json_persistente(
      "clientes_pedidos",
      ARQ_CLIENTES_PEDIDOS,
      st.session_state.clientes_pedidos,
  )


def recarregar_mensagens_frescas():
  st.session_state.mensagens = ler_json_persistente(
      "mensagens", ARQ_MENSAGENS, []
  )


def recarregar_estoque_fresco():
  df_padrao = pd.DataFrame(
      columns=[
          "Codigo_Barras",
          "Produto",
          "Descricao",
          "Unidades_Embalagem",
          "Tipo_Item",
          "Setor",
          "Quantidade",
          "Limite_Minimo",
          "Lote",
          "Fabricacao",
          "Validade",
          "Ultima_Modificacao",
          "Modificado_Por",
      ]
  )
  st.session_state.estoque = ler_df_persistente(
      "estoque", ARQ_ESTOQUE, df_padrao
  )


def carregar_bg_base64(caminho: str):
  if caminho and os.path.exists(caminho):
    try:
      with open(caminho, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
      return None
  return None


# --- INICIALIZAÇÃO COM CARREGAMENTO PERSISTENTE ---
if "users" not in st.session_state:
  users_padrao = {
      "admin": {
          "senha_hash": hash_senha("1234"),
          "perfil": "Administrador",
          "pode_cadastrar": True,
          "pode_excluir": True,
          "pode_movimentar": True,
      },
      "operador": {
          "senha_hash": hash_senha("abcd"),
          "perfil": "Operador",
          "pode_cadastrar": False,
          "pode_excluir": False,
          "pode_movimentar": True,
      },
  }
  carregados = ler_json_persistente("users", ARQ_USERS, users_padrao)
  migrado = False
  for _, info in carregados.items():
    if "senha_hash" not in info and "senha" in info:
      info["senha_hash"] = hash_senha(info.pop("senha"))
      migrado = True
  st.session_state.users = carregados
  if not os.path.exists(ARQ_USERS) or migrado:
    salvar_users()

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.perfil = ""

if "config_visual" not in st.session_state:
  cfg_padrao = {
      "tamanho_fonte": "16px",
      "cor_fundo_tabela": "#f9f9f9",
      "cor_texto": "#31333F",
      "fundo_app": "Gradiente Azul Moderno",
      "fundo_login": "Gradiente Azul Moderno",
      "url_papel_parede": "",
  }
  st.session_state.config_visual = ler_json_persistente(
      "config_visual", ARQ_CONFIG, cfg_padrao
  )
  st.session_state.config_visual.setdefault("url_papel_parede", "")
  if not os.path.exists(ARQ_CONFIG):
    salvar_config()

if "historico" not in st.session_state:
  hist_padrao = pd.DataFrame(
      columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"]
  )
  st.session_state.historico = ler_df_persistente(
      "historico", ARQ_HIST, hist_padrao
  )
  if not os.path.exists(ARQ_HIST):
    salvar_historico()

if "mensagens" not in st.session_state:
  st.session_state.mensagens = ler_json_persistente(
      "mensagens", ARQ_MENSAGENS, []
  )
  if not os.path.exists(ARQ_MENSAGENS):
    salvar_mensagens()

if "clientes" not in st.session_state:
  clientes_padrao = [
      {
          "razao_social": "Neriah Comercio de Alimentos LTDA",
          "nome_fantasia": "Neriah Comércio",
          "cnpj": "12.345.678/0001-99",
          "endereco": "Rua Principal, 100 - Florianópolis - SC",
          "contacto": "(48) 99999-9999",
      }
  ]
  st.session_state.clientes = ler_json_persistente(
      "clientes", ARQ_CLIENTES, clientes_padrao
  )
  if not os.path.exists(ARQ_CLIENTES):
    salvar_clientes()

if "clientes_pedidos" not in st.session_state:
  st.session_state.clientes_pedidos = ler_json_persistente(
      "clientes_pedidos", ARQ_CLIENTES_PEDIDOS, []
  )
  if not os.path.exists(ARQ_CLIENTES_PEDIDOS):
    salvar_clientes_pedidos()

if "agenda_eventos" not in st.session_state:
  st.session_state.agenda_eventos = []

if "setores" not in st.session_state:
  setores_padrao = ["Armazém Central", "Câmara Fria", "Secos e Molhados"]
  st.session_state.setores = ler_json_persistente(
      "setores", ARQ_SETORES, setores_padrao
  )
  if not os.path.exists(ARQ_SETORES):
    salvar_setores()

if "pedidos_ativos" not in st.session_state:
  st.session_state.pedidos_ativos = {}

if "estoque" not in st.session_state:
  estoque_padrao = pd.DataFrame({
      "Codigo_Barras": ["789101", "789102", "789103"],
      "Produto": [
          "Calzone Chocolate (12 un)",
          "Farinha de Trigo (Kg)",
          "Óleo de Soja (L)",
      ],
      "Descricao": [
          "Calzone doce de chocolate",
          "Farinha tipo 1 refinada",
          "Óleo vegetal de soja",
      ],
      "Unidades_Embalagem": [12, 10, 20],
      "Tipo_Item": ["Produto Acabado", "Matéria-Prima", "Insumo"],
      "Setor": ["Secos e Molhados", "Secos e Molhados", "Câmara Fria"],
      "Quantidade": [40, 30, 20],
      "Limite_Minimo": [10, 25, 5],
      "Lote": ["LOT-2026-A", "LOT-2026-B", "LOT-2026-C"],
      "Fabricacao": ["2026-10-01", "2026-09-15", "2026-10-10"],
      "Validade": ["2026-11-15", "2027-05-20", "2026-11-10"],
      "Ultima_Modificacao": ["2026-11-01", "2026-11-05", "2026-11-10"],
      "Modificado_Por": ["admin", "operador", "admin"],
  })
  st.session_state.estoque = ler_df_persistente(
      "estoque", ARQ_ESTOQUE, estoque_padrao
  )
  if not os.path.exists(ARQ_ESTOQUE):
    salvar_estoque()

if "Lote" not in st.session_state.estoque.columns:
  st.session_state.estoque["Lote"] = "LOT-GERAL"
st.session_state.estoque["Codigo_Barras"] = (
    st.session_state.estoque["Codigo_Barras"].astype(str).str.strip()
)
st.session_state.estoque["Quantidade"] = (
    pd.to_numeric(st.session_state.estoque["Quantidade"], errors="coerce")
    .fillna(0)
    .astype(int)
)
st.session_state.estoque["Limite_Minimo"] = (
    pd.to_numeric(st.session_state.estoque["Limite_Minimo"], errors="coerce")
    .fillna(0)
    .astype(int)
)

# Capturar código vindo do leitor ótico da câmara em tempo real
if "scanned_code" in st.query_params:
  st.session_state["codigo_lido_ativo"] = str(
      st.query_params["scanned_code"]
  ).strip()
  st.query_params.clear()
  st.rerun()

# --- VISUAL, FONTES, PAPEL DE PAREDE & BARRA DE ROLAGEM ---
cfg = st.session_state.config_visual
bg_css = TEMAS_FUNDO.get(
    cfg.get("fundo_app", "Gradiente Azul Moderno"),
    TEMAS_FUNDO["Gradiente Azul Moderno"],
)
url_wp = cfg.get("url_papel_parede", "").strip()
b64_wp_local = carregar_bg_base64("papel_parede.jpg")

if url_wp:
  fundo_efetivo = (
      f'linear-gradient(rgba(245, 247, 250, 0.85), rgba(245, 247, 250, 0.85)),'
      f' url("{url_wp}")'
  )
elif b64_wp_local:
  fundo_efetivo = (
      f"linear-gradient(rgba(245, 247, 250, 0.85), rgba(245, 247, 250, 0.85)),"
      f' url("data:image/jpeg;base64,{b64_wp_local}")'
  )
else:
  fundo_efetivo = bg_css

st.markdown(
   cfg = st.session_state.config_visual
bg_css = TEMAS_FUNDO.get(
    cfg.get("fundo_app", "Gradiente Azul Moderno"),
    TEMAS_FUNDO["Gradiente Azul Moderno"],
)
url_wp = cfg.get("url_papel_parede", "").strip()
b64_wp_local = carregar_bg_base64("papel_parede.jpg")

if url_wp:
  fundo_efetivo = (
      f'linear-gradient(rgba(245, 247, 250, 0.85), rgba(245, 247, 250, 0.85)),'
      f' url("{url_wp}")'
  )
elif b64_wp_local:
  fundo_efetivo = (
      f"linear-gradient(rgba(245, 247, 250, 0.85), rgba(245, 247, 250, 0.85)),"
      f' url("data:image/jpeg;base64,{b64_wp_local}")'
  )
else:
  fundo_efetivo = bg_css

st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    html, body, .stApp, p, label, input, textarea, select, button {{
        font-family: 'Poppins', sans-serif !important;
    }}
    html, body, [class*="css"] {{
        font-size: {cfg.get('tamanho_fonte', '16px')} !important;
        color: {cfg.get('cor_texto', '#31333F')} !important;
    }}
    .stApp {{
        background: {fundo_efetivo} !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    section[data-testid="stSidebar"] {{
        min-width: 270px !important;
        overflow-y: auto !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        overflow-y: auto !important;
        max-height: 100vh !important;
    }}
    .stDataFrame {{
        background-color: {cfg.get('cor_fundo_tabela', '#f9f9f9')} !important;
    }}
    div[data-testid="stVerticalBlock"] > div[style*="border-color"],
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 14px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)
