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

# --- SISTEMA DE LOGIN ---
if not st.session_state.logged_in:
  bg_login_css = TEMAS_FUNDO.get(
      cfg.get("fundo_login", "Gradiente Azul Moderno"),
      TEMAS_FUNDO["Gradiente Azul Moderno"],
  )
  st.markdown(
      f"""
        <style>
        .stApp {{
            background: {bg_login_css} !important;
            background-attachment: fixed !important;
        }}
        </style>
        """,
      unsafe_allow_html=True,
  )

  col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
  with col_l2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.container(border=True):
      st.markdown(
          "<h2 style='text-align: center; color: #2c3e50; margin-bottom: 0px;'>🍲"
          " RBM Alimentos</h2>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; color: #666; font-size: 14px;'>Controlo"
          " de Estoque & Expedição</p>",
          unsafe_allow_html=True,
      )
      st.markdown("---")

      user_input = st.text_input("👤 Utilizador", key="login_user").strip()
      pass_input = st.text_input(
          "🔑 Senha de Acesso", type="password", key="login_pass"
      )

      st.markdown("<br>", unsafe_allow_html=True)
      if st.button(
          "🚀 Entrar no Sistema", type="primary", use_container_width=True
      ):
        u_dados = st.session_state.users.get(user_input)
        senha_armazenada = (
            u_dados.get("senha_hash", u_dados.get("senha", ""))
            if u_dados
            else ""
        )
        if u_dados and verificar_senha(pass_input, senha_armazenada):
          if "senha_hash" not in u_dados:
            u_dados["senha_hash"] = hash_senha(pass_input)
            u_dados.pop("senha", None)
            salvar_users()
          st.session_state.logged_in = True
          st.session_state.username = user_input
          st.session_state.perfil = u_dados["perfil"]
          st.success("Login efetuado com sucesso!")
          st.rerun()
        else:
          st.error("Utilizador ou senha incorretos.")
  st.stop()

permissoes_atuais = st.session_state.users.get(
    st.session_state.username,
    {
        "pode_cadastrar": True,
        "pode_excluir": True,
        "pode_movimentar": True,
    },
)

# --- BARRA LATERAL ---
st.sidebar.title(f"👤 {st.session_state.username}")
st.sidebar.caption(f"Perfil: **{st.session_state.perfil}**")
st.sidebar.caption(
    "☁️ Cloud Sync: **Ativo (Google Sheets)**"
    if _gsheets_ativo()
    else "💾 Modo: **Local / Sessão**"
)

recarregar_mensagens_frescas()
msgs_nao_lidas = [
    m
    for m in st.session_state.mensagens
    if m["para"] == st.session_state.username and not m.get("lida", False)
]
num_novas = len(msgs_nao_lidas)

if num_novas > 0:
  st.sidebar.warning(f"🔔 Tem {num_novas} nova(s) mensagem(ns)!")

opcoes_menu = [
    "🍲 Consultar Stock & Setores",
    "➕ Entradas / Saídas (Expedição)",
    "🏷️ Gerar Etiquetas (Lotes)",
    "📋 Gestão de Pedidos & Check-list",
    "👥 Gestão de Clientes & Pedidos",
    f"💬 Mensagens & Bate-Papo ({num_novas})",
    "📊 Romaneios & Relatórios",
    "📜 Histórico de Auditoria",
    "⚙️ Configuração",
]

if st.session_state.perfil == "Administrador":
  opcoes_menu.insert(1, "⚙️ Painel do Administrador & Agenda")

menu = st.sidebar.selectbox("Navegação do Armazém", opcoes_menu)

if st.sidebar.button("Terminar Sessão"):
  st.session_state.logged_in = False
  st.rerun()

df = st.session_state.estoque

if "Fabricacao" not in df.columns:
  df["Fabricacao"] = datetime.date.today().strftime("%Y-%m-%d")
if "Validade" not in df.columns:
  df["Validade"] = datetime.date.today().strftime("%Y-%m-%d")

# --- 1. PAINEL DO ADMINISTRADOR ---
if menu == "⚙️ Painel do Administrador & Agenda":
  if st.session_state.perfil != "Administrador":
    st.error("⚠️ Acesso restrito!")
    st.stop()

  st.markdown("## ⚙️ Painel de Controlo do Administrador")
  tab_adm1, tab_adm2, tab_adm3, tab_adm4, tab_adm5, tab_adm6 = st.tabs([
      "👥 Utilizadores",
      "🏢 Setores",
      "📅 Agenda",
      "✏️ Editar Itens",
      "💾 Backup & Restauro",
      "🎨 Visual & Eliminar",
  ])

  with tab_adm1:
    with st.container(border=True):
      st.subheader("Registar ou Modificar Utilizador")
      novo_user = st.text_input("Nome do Utilizador").strip()
      nova_senha = st.text_input("Senha de Acesso", type="password")
      novo_perfil = st.selectbox("Perfil", ["Operador", "Administrador"])
      col_p1, col_p2, col_p3 = st.columns(3)
      with col_p1:
        pode_cad = st.checkbox("Pode Cadastrar", value=True)
      with col_p2:
        pode_exc = st.checkbox("Pode Excluir", value=False)
      with col_p3:
        pode_mov = st.checkbox("Pode Movimentar", value=True)
      if st.button("Guardar Utilizador"):
        if novo_user and nova_senha:
          st.session_state.users[novo_user] = {
              "senha_hash": hash_senha(nova_senha),
              "perfil": novo_perfil,
              "pode_cadastrar": pode_cad,
              "pode_excluir": pode_exc,
              "pode_movimentar": pode_mov,
          }
          salvar_users()
          st.success(f"Utilizador '{novo_user}' guardado com sucesso!")
        else:
          st.error("Preencha o nome e a senha.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Utilizadores Atuais")
    for u, dados in list(st.session_state.users.items()):
      with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
          st.write(f"👤 **{u}** ({dados['perfil']})")
        with c2:
          if u != "admin":
            if st.button(f"Excluir #{u}", key=f"del_u_{u}"):
              del st.session_state.users[u]
              salvar_users()
              st.rerun()

  with tab_adm2:
    with st.container(border=True):
      st.subheader("Gestão de Setores")
      novo_setor = st.text_input("Nome do Novo Setor", key="in_setor")
      if st.button("Adicionar Setor"):
        if novo_setor and novo_setor.strip():
          if novo_setor.strip() not in st.session_state.setores:
            st.session_state.setores.append(novo_setor.strip())
            salvar_setores()
            st.success("Setor criado e guardado com sucesso!")
            st.rerun()
          else:
            st.error("Este setor já existe.")
        else:
          st.error("Nome inválido.")
    st.markdown("<br>", unsafe_allow_html=True)
    for s in list(st.session_state.setores):
      with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
          st.write(f"🏭 {s}")
        with c2:
          if len(st.session_state.setores) > 1:
            if st.button("Excluir", key=f"del_s_{s}"):
              st.session_state.setores.remove(s)
              salvar_setores()
              st.rerun()

  with tab_adm3:
    with st.container(border=True):
      st.subheader("📅 Agenda de Eventos")
      data_evento = st.date_input("Data")
      desc_evento = st.text_input("Descrição")
      if st.button("Adicionar Evento"):
        if desc_evento and desc_evento.strip():
          st.session_state.agenda_eventos.append(
              {"data": str(data_evento), "evento": desc_evento.strip()}
          )
          st.success("Adicionado!")
        else:
          st.error("Informe uma descrição para o evento.")
    st.markdown("<br>", unsafe_allow_html=True)
    for ev in st.session_state.agenda_eventos:
      st.write(f"📅 **{ev['data']}**: {ev['evento']}")

  with tab_adm4:
    with st.container(border=True):
      st.subheader("✏️ Edição Rápida de Itens Cadastrados")
      if df.empty:
        st.info("Nenhum produto disponível para editar.")
      else:
        prod_editar = st.selectbox(
            "Selecione o produto", df["Produto"].tolist(), key="sel_ed"
        )
        if prod_editar:
          idx_ed = df[df["Produto"] == prod_editar].index[0]
          nn = st.text_input(
              "Nome", value=str(df.loc[idx_ed, "Produto"]), key="ed_n"
          )
          nd = st.text_area(
              "Descrição", value=str(df.loc[idx_ed, "Descricao"]), key="ed_d"
          )
          ne = st.number_input(
              "Embalagem",
              min_value=1,
              value=int(df.loc[idx_ed, "Unidades_Embalagem"]),
              key="ed_e",
          )
          nm = st.number_input(
              "Mínimo",
              min_value=0,
              value=int(df.loc[idx_ed, "Limite_Minimo"]),
              key="ed_m",
          )
          ns = st.selectbox(
              "Setor",
              st.session_state.setores,
              index=(
                  st.session_state.setores.index(df.loc[idx_ed, "Setor"])
                  if df.loc[idx_ed, "Setor"] in st.session_state.setores
                  else 0
              ),
              key="ed_s",
          )
          if st.button("Guardar Alterações"):
            if not nn.strip():
              st.error("⚠️ O nome do produto não pode ficar em branco.")
            else:
              recarregar_estoque_fresco()
              df_atual = st.session_state.estoque
              mask_ed = df_atual["Produto"] == prod_editar
              if mask_ed.any():
                idx_real = df_atual[mask_ed].index[0]
                df_atual.loc[idx_real, "Produto"] = nn.strip()
                df_atual.loc[idx_real, "Descricao"] = nd.strip()
                df_atual.loc[idx_real, "Unidades_Embalagem"] = int(ne)
                df_atual.loc[idx_real, "Limite_Minimo"] = int(nm)
                df_atual.loc[idx_real, "Setor"] = ns
                df_atual.loc[idx_real, "Ultima_Modificacao"] = (
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                )
                df_atual.loc[idx_real, "Modificado_Por"] = (
                    st.session_state.username
                )
                salvar_estoque()
                st.success("Atualizado e guardado com sucesso!")
                st.rerun()

  with tab_adm5:
    with st.container(border=True):
      st.subheader("💾 Backup e Restauro de Dados")
      csv_data = df.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          label="📥 Descarregar Backup do Stock (CSV)",
          data=csv_data,
          file_name=f"backup_estoque_{datetime.date.today()}.csv",
          mime="text/csv",
      )
      st.markdown("---")
      uploaded_backup = st.file_uploader(
          "Restaurar Stock através de Ficheiro CSV", type=["csv"]
      )
      if uploaded_backup is not None:
        if st.button("🔄 Confirmar Restauro do Stock"):
          try:
            df_restaurado = pd.read_csv(uploaded_backup)
            colunas_obrigatorias = {"Produto", "Codigo_Barras", "Quantidade"}
            if not colunas_obrigatorias.issubset(set(df_restaurado.columns)):
              st.error(
                  "⚠️ O CSV enviado não contém as colunas obrigatórias"
                  " (Produto, Codigo_Barras, Quantidade)."
              )
            else:
              st.session_state.estoque = df_restaurado
              salvar_estoque()
              st.success("Stock restaurado com sucesso!")
              st.rerun()
          except Exception as e:
            st.error(f"Erro ao ler o ficheiro: {e}")

  with tab_adm6:
    with st.container(border=True):
      st.subheader("🎨 Estilo & Eliminação de Produtos")
      if df.empty:
        st.info("Nenhum produto para eliminar.")
      else:
        prod_ex = st.selectbox(
            "Eliminar Produto do Catálogo", df["Produto"].tolist(), key="ex_p"
        )
        confirmar_ex = st.checkbox(
            "Confirmo que desejo eliminar este produto permanentemente",
            key="chk_ex_prod",
        )
        if st.button("Confirmar Eliminação"):
          if not confirmar_ex:
            st.warning("⚠️ Marque a caixa de confirmação antes de eliminar.")
          else:
            recarregar_estoque_fresco()
            st.session_state.estoque = st.session_state.estoque[
                st.session_state.estoque["Produto"] != prod_ex
            ].reset_index(drop=True)
            salvar_estoque()
            st.success("Produto eliminado com sucesso!")
            st.rerun()


# --- PÁGINA DE CONFIGURAÇÃO VISUAL ---
elif menu == "⚙️ Configuração":
  st.markdown("## ⚙️ Configurações Visuais & Temas do Sistema")
  st.markdown(
      "Personalize os papéis de parede, cores e tamanhos do aplicativo e da"
      " tela de login com **pré-visualização ao vivo** antes de aplicar."
  )

  col_cfg1, col_cfg2 = st.columns([1, 1])

  with col_cfg1:
    with st.container(border=True):
      st.subheader("🎨 Parâmetros de Estilo")
      lista_temas = list(TEMAS_FUNDO.keys())

      idx_app = (
          lista_temas.index(cfg.get("fundo_app", "Gradiente Azul Moderno"))
          if cfg.get("fundo_app", "Gradiente Azul Moderno") in lista_temas
          else 0
      )
      idx_login = (
          lista_temas.index(cfg.get("fundo_login", "Gradiente Azul Moderno"))
          if cfg.get("fundo_login", "Gradiente Azul Moderno") in lista_temas
          else 0
      )

      prev_fundo_app = st.selectbox(
          "🖼️ Papel de Parede / Tema do Aplicativo Principal",
          lista_temas,
          index=idx_app,
      )
      prev_fundo_login = st.selectbox(
          "🔐 Papel de Parede / Tema da Página de Login",
          lista_temas,
          index=idx_login,
      )
      prev_url_wp = st.text_input(
          "🌐 URL de Imagem de Papel de Parede (opcional)",
          value=cfg.get("url_papel_parede", ""),
          placeholder="https://exemplo.com/fundo.jpg",
      )

      tamanhos_disponiveis = ["14px", "15px", "16px", "18px", "20px"]
      idx_tam = (
          tamanhos_disponiveis.index(cfg.get("tamanho_fonte", "16px"))
          if cfg.get("tamanho_fonte", "16px") in tamanhos_disponiveis
          else 2
      )
      prev_tamanho = st.selectbox(
          "📏 Tamanho da Fonte Global", tamanhos_disponiveis, index=idx_tam
      )

      prev_cor_texto = st.text_input(
          "✍️ Cor do Texto (Hex ou Nome)",
          value=cfg.get("cor_texto", "#31333F"),
      )
      prev_cor_tabela = st.text_input(
          "📊 Cor de Fundo das Tabelas",
          value=cfg.get("cor_fundo_tabela", "#f9f9f9"),
      )

      st.markdown("<br>", unsafe_allow_html=True)
      if st.button(
          "💾 Aplicar e Guardar Configurações Definitivas", type="primary"
      ):
        st.session_state.config_visual["fundo_app"] = prev_fundo_app
        st.session_state.config_visual["fundo_login"] = prev_fundo_login
        st.session_state.config_visual["url_papel_parede"] = prev_url_wp.strip()
        st.session_state.config_visual["tamanho_fonte"] = prev_tamanho
        st.session_state.config_visual["cor_texto"] = prev_cor_texto.strip()
        st.session_state.config_visual["cor_fundo_tabela"] = (
            prev_cor_tabela.strip()
        )
        salvar_config()
        st.success("✨ Configurações aplicadas e guardadas com sucesso!")
        st.rerun()

  with col_cfg2:
    st.subheader("👁️ Pré-visualização ao Vivo")
    bg_preview_css = (
        f'linear-gradient(rgba(245, 247, 250, 0.85), rgba(245, 247, 250, 0.85)), url("{prev_url_wp.strip()}")'
        if prev_url_wp.strip()
        else TEMAS_FUNDO.get(
            prev_fundo_app, TEMAS_FUNDO["Gradiente Azul Moderno"]
        )
    )
    preview_html = """
        <div style="background: {}; background-size: cover; background-position: center; padding: 25px; border-radius: 14px; border: 2px dashed #007bff; color: {}; font-size: {}; font-family: 'Poppins', sans-serif;">
            <h3 style="margin-top:0; color: {};">🔍 Exemplo de Cartão RBM</h3>
            <p>Este é o aspeto do texto principal com a fonte <b>{}</b>.</p>
            <div style="background-color: {}; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-top: 10px;">
                <b>📊 Pré-visualização de Tabela / Bloco:</b><br>
                Produto Exemplo: Calzone Chocolate (12 un)<br>
                Stock: 40 unidades (Setor: Secos e Molhados)
            </div>
            <button style="margin-top: 15px; background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer;">Botão de Exemplo</button>
        </div>
        """.format(
        bg_preview_css,
        prev_cor_texto,
        prev_tamanho,
        prev_cor_texto,
        prev_tamanho,
        prev_cor_tabela,
    )
    st.markdown(preview_html, unsafe_allow_html=True)


# --- 2. CONSULTAR STOCK & KPIs ---
elif menu == "🍲 Consultar Stock & Setores":
  st.markdown("## 🍲 Consulta de Stock, Lotes & Indicadores (KPIs)")
if st.session_state.perfil == "Administrador":
    st.markdown("---")
    st.subheader(
        "✏️ Ajuste Direto de Quantidade (Exclusivo Administrador)"
    )
    st.caption(
        "Altere apenas o valor da coluna **Quantidade** diretamente na"
        " tabela abaixo e clique em **Salvar Quantidades**."
    )

    df_edit_base = df_f.copy()
    colunas_editor = [
        c
        for c in [
            "Codigo_Barras",
            "Produto",
            "Setor",
            "Lote",
            "Quantidade",
            "Limite_Minimo",
            "Validade",
        ]
        if c in df_edit_base.columns
    ]

    df_editado = st.data_editor(
        df_edit_base[colunas_editor],
        use_container_width=True,
        hide_index=True,
        key="editor_qtd_admin",
        disabled=[c for c in colunas_editor if c != "Quantidade"],
    )

    if st.button("💾 Salvar Quantidades", type="primary"):
      recarregar_estoque_fresco()
      df_est = st.session_state.estoque
      data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
      alteracoes = 0

      for _, linha_ed in df_editado.iterrows():
        nova_qtd = int(
            pd.to_numeric(linha_ed["Quantidade"], errors="coerce") or 0
        )
        if nova_qtd < 0:
          nova_qtd = 0

        mask = (
            df_est["Codigo_Barras"].astype(str).str.strip()
            == str(linha_ed["Codigo_Barras"]).strip()
        ) & (
            df_est["Produto"].astype(str).str.strip()
            == str(linha_ed["Produto"]).strip()
        )
        if "Lote" in df_est.columns and "Lote" in linha_ed:
          mask = mask & (
              df_est["Lote"].astype(str).str.strip()
              == str(linha_ed["Lote"]).strip()
          )

        if mask.any():
          idx_alvo = df_est[mask].index[0]
          qtd_anterior = int(df_est.loc[idx_alvo, "Quantidade"])
          if nova_qtd != qtd_anterior:
            df_est.loc[idx_alvo, "Quantidade"] = nova_qtd
            df_est.loc[idx_alvo, "Ultima_Modificacao"] = data_atual
            df_est.loc[idx_alvo, "Modificado_Por"] = st.session_state.username
            alteracoes += 1

            nova_hist = pd.DataFrame(
                [[
                    data_atual,
                    st.session_state.username,
                    f"Ajuste Direto Qtd ({qtd_anterior} -> {nova_qtd})",
                    df_est.loc[idx_alvo, "Produto"],
                    abs(nova_qtd - qtd_anterior),
                ]],
                columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
            )
            st.session_state.historico = pd.concat(
                [st.session_state.historico, nova_hist], ignore_index=True
            )

      if alteracoes > 0:
        salvar_estoque()
        salvar_historico()
        st.success(
            f"✅ {alteracoes} quantidade(s) atualizada(s) com sucesso!"
        )
        st.rerun()
      else:
        st.info("Nenhuma alteração de quantidade foi feita.")
  hoje_str = datetime.date.today().strftime("%Y-%m-%d")
  total_skus = len(df)
  total_qtd = int(df["Quantidade"].sum()) if not df.empty else 0
  criticos = (
      len(df[df["Quantidade"] <= df["Limite_Minimo"]]) if not df.empty else 0
  )
  vencidos = (
      len(df[df["Validade"].astype(str) <= hoje_str]) if not df.empty else 0
  )

  k1, k2, k3, k4 = st.columns(4)
  k1.metric("📦 Total de Produtos (SKUs)", total_skus)
  k2.metric("📊 Quantidade Total em Stock", total_qtd)
  k3.metric("⚠️ Abaixo do Mínimo", criticos, delta_color="inverse")
  k4.metric("🚨 Lotes Vencidos / Vencendo", vencidos, delta_color="inverse")

  st.markdown("---")

  setor_filtro = st.selectbox(
      "Filtrar por Setor", ["Todos os Setores"] + st.session_state.setores
  )
  pesquisa = st.text_input(
      "🔍 Pesquisar por Produto, Lote ou Código de Barras", ""
  )

  df_f = df.copy()
  if setor_filtro != "Todos os Setores":
    df_f = df_f[df_f["Setor"] == setor_filtro]
  if pesquisa:
    df_f = df_f[
        df_f["Produto"].astype(str).str.contains(pesquisa, case=False, na=False)
        | df_f["Codigo_Barras"]
        .astype(str)
        .str.contains(pesquisa, case=False, na=False)
        | df_f["Lote"].astype(str).str.contains(pesquisa, case=False, na=False)
    ]

  def estilo_alerta(row):
    val = str(row.get("Validade", hoje_str))
    if row["Quantidade"] <= row["Limite_Minimo"] or val <= hoje_str:
      return [
          "color: red; font-weight: bold; background-color: #ffe6e6;"
      ] * len(row)
    return [""] * len(row)

  st.dataframe(
      df_f.style.apply(estilo_alerta, axis=1), use_container_width=True
  )


# --- 3. ENTRADAS E SAÍDAS ---
elif menu == "➕ Entradas / Saídas (Expedição)":
  st.markdown(
      "## ➕ Entradas, Saídas, Leitura por Câmara & Controlo FIFO (Lotes)"
  )

  if not permissoes_atuais.get("pode_movimentar", True):
    st.error("Sem permissão para movimentar stock.")
  else:
    if (
        st.session_state.perfil == "Administrador"
        and permissoes_atuais.get("pode_cadastrar", True)
    ):
      with st.container(border=True):
        cadastrar_novo_manual = st.checkbox(
            "➕ [Admin] Adicionar Novo Produto / Lote ao Catálogo"
        )
        if cadastrar_novo_manual:
          st.subheader("Registo de Novo Item / Lote no Catálogo")
          col_m1, col_m2 = st.columns(2)
          with col_m1:
            m_nome = st.text_input("Nome do Produto")
            m_cod = st.text_input("Código de Barras")
            m_lote = st.text_input(
                "Número do Lote", value=f"LOT-{datetime.date.today().year}-01"
            )
            m_desc = st.text_area("Descrição")
          with col_m2:
            m_emb = st.number_input(
                "Unidades por Embalagem", min_value=1, value=1
            )
            m_tipo = st.selectbox(
                "Tipo",
                ["Produto Acabado", "Matéria-Prima", "Insumo", "Embalagem"],
            )
            m_setor = st.selectbox(
                "Setor de Armazenamento", st.session_state.setores
            )
            m_min = st.number_input("Limite Mínimo", min_value=0, value=10)

          col_d1, col_d2 = st.columns(2)
          with col_d1:
            m_fab = st.date_input(
                "Data de Fabricação", datetime.date.today(), key="novo_fab"
            )
          with col_d2:
            m_val = st.date_input(
                "Data de Validade", datetime.date.today(), key="novo_val"
            )

          if st.button("Guardar Novo Produto / Lote"):
            nome_limpo = m_nome.strip()
            cod_limpo = m_cod.strip()
            lote_limpo = m_lote.strip()
            if not nome_limpo or not cod_limpo or not lote_limpo:
              st.error(
                  "⚠️ Preencha Nome do Produto, Código de Barras e Número do"
                  " Lote."
              )
            elif m_val < m_fab:
              st.error(
                  "⚠️ A data de validade não pode ser anterior à data de"
                  " fabricação."
              )
            else:
              recarregar_estoque_fresco()
              df_est = st.session_state.estoque
              duplicado = (
                  (df_est["Codigo_Barras"].astype(str).str.strip() == cod_limpo)
                  & (df_est["Lote"].astype(str).str.strip() == lote_limpo)
              ).any()
              if duplicado:
                st.error(
                    f"⚠️ Já existe o código '{cod_limpo}' com o lote"
                    f" '{lote_limpo}'."
                )
              else:
                nova_l = pd.DataFrame({
                    "Codigo_Barras": [cod_limpo],
                    "Produto": [nome_limpo],
                    "Descricao": [m_desc.strip()],
                    "Unidades_Embalagem": [int(m_emb)],
                    "Tipo_Item": [m_tipo],
                    "Setor": [m_setor],
                    "Quantidade": [0],
                    "Limite_Minimo": [int(m_min)],
                    "Lote": [lote_limpo],
                    "Fabricacao": [str(m_fab)],
                    "Validade": [str(m_val)],
                    "Ultima_Modificacao": [
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    ],
                    "Modificado_Por": [st.session_state.username],
                })
                st.session_state.estoque = pd.concat(
                    [df_est, nova_l], ignore_index=True
                )
                salvar_estoque()
                st.success(
                    f"Produto e Lote '{lote_limpo}' registados com sucesso no"
                    f" setor '{m_setor}'!"
                )
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
      st.subheader("📦 Movimentar Stock (Entrada / Saída com Regra FIFO)")

      if not df.empty:
        df_fifo = df.sort_values(by="Validade", ascending=True)
        produto_sugestao = df_fifo.iloc[0]["Produto"]
        lote_sugestao = df_fifo.iloc[0]["Lote"]
        val_sugestao = df_fifo.iloc[0]["Validade"]
        st.info(
            f"💡 **Recomendação FIFO (Primeiro a Vencer):** O lote mais antigo"
            f" a expirar é **{lote_sugestao}** do produto **{produto_sugestao}**"
            f" (Validade: {val_sugestao}). Priorize a expedição deste lote!"
        )

      modo_mov = st.radio(
          "Método de Identificação",
          [
              "Selecionar na Lista",
              "📷 Leitor Ótico com Câmara Traseira (Tempo Real)",
              "Digitar Código de Barras",
          ],
          horizontal=True,
      )

      produto_selecionado = None

      if modo_mov == "Selecionar na Lista":
        if not df.empty:
          produto_selecionado = st.selectbox(
              "Produto", df["Produto"].tolist(), key="sel_mov_l"
          )
      elif modo_mov == "📷 Leitor Ótico com Câmara Traseira (Tempo Real)":
        st.markdown(
            "💡 Clique abaixo para abrir a câmara traseira. Ao apontar para"
            " a etiqueta, o código será lido instantaneamente:"
        )

        scanner_html = """
            <div style="text-align: center; background: #f8f9fa; padding: 15px; border-radius: 12px; border: 1px solid #ddd;">
                <div id="reader" style="width:100%; max-width:320px; margin:auto; border-radius: 8px; overflow: hidden;"></div>
                <br>
                <button id="start-btn" onclick="startScanner()" style="width:100%; padding:14px; background:#28a745; color:white; border:none; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer;">📸 Ligar Câmara Traseira</button>
                <button id="stop-btn" onclick="stopScanner()" style="display:none; width:100%; padding:14px; background:#dc3545; color:white; border:none; border-radius:8px; font-weight:bold; font-size:16px; cursor:pointer; margin-top:10px;">🛑 Desligar Câmara</button>
            </div>
            <script src="https://unpkg.com/html5-qrcode"></script>
            <script>
            let html5QrCode = null;
            function startScanner() {
                document.getElementById('start-btn').style.display = 'none';
                document.getElementById('stop-btn').style.display = 'block';
                html5QrCode = new Html5Qrcode("reader");
                html5QrCode.start(
                    { facingMode: "environment" },
                    { fps: 15, qrbox: { width: 250, height: 120 } },
                    (decodedText, decodedResult) => {
                        html5QrCode.stop().then(() => {
                            window.parent.location.search = '?scanned_code=' + encodeURIComponent(decodedText);
                        }).catch(err => {
                            window.parent.location.search = '?scanned_code=' + encodeURIComponent(decodedText);
                        });
                    },
                    (errorMessage) => {}
                ).catch(err => {
                    alert("Erro ao aceder à câmara: " + err);
                    document.getElementById('start-btn').style.display = 'block';
                    document.getElementById('stop-btn').style.display = 'none';
                });
            }
            function stopScanner() {
                if (html5QrCode) {
                    html5QrCode.stop().then(() => {
                        document.getElementById('start-btn').style.display = 'block';
                        document.getElementById('stop-btn').style.display = 'none';
                    }).catch(err => { console.log(err); });
                }
            }
            </script>
            """
        components.html(scanner_html, height=420)

        cod_lido = st.session_state.get("codigo_lido_ativo", "")
        if cod_lido:
          match = df[
              df["Codigo_Barras"].astype(str).str.strip() == cod_lido.strip()
          ]
          if not match.empty:
            produto_selecionado = match.iloc[0]["Produto"]
            st.success(
                f"🎯 Produto Encontrado: **{produto_selecionado}** (Lote:"
                f" {match.iloc[0].get('Lote', 'N/A')})"
            )
          else:
            st.error("⚠️ Código de barras detetado não consta no stock.")
      else:
        bc = st.text_input(
            "Digite o Código de Barras", placeholder="Ex: 789101..."
        ).strip()
        if bc:
          match = df[df["Codigo_Barras"].astype(str).str.strip() == bc]
          if not match.empty:
            produto_selecionado = match.iloc[0]["Produto"]
            st.success(
                f"Encontrado: **{produto_selecionado}** (Lote:"
                f" {match.iloc[0].get('Lote', 'N/A')})"
            )
          else:
            st.error("Código de barras não registado no sistema.")

      if produto_selecionado:
        st.markdown("---")
        idx_ref = df[df["Produto"] == produto_selecionado].index[0]
        lote_atual_prod = str(df.loc[idx_ref, "Lote"])

        tipo_op = st.radio(
            "Operação",
            ["Recebimento (Entrada)", "Baixa (Saída)"],
            horizontal=True,
        )

        col_q1, col_q2, col_q3 = st.columns(3)
        with col_q1:
          qtd_op = st.number_input(
              "Quantidade a Movimentar", min_value=1, value=1, key="qtd_mov_val"
          )
        with col_q2:
          novo_lote_mov = st.text_input("Nº do Lote", value=lote_atual_prod)
        with col_q3:
          data_fab_mov = st.date_input(
              "Fabricação", datetime.date.today(), key="fab_mov_dt"
          )
          data_val_mov = st.date_input(
              "Validade", datetime.date.today(), key="val_mov_dt"
          )

        if st.button("🚀 Confirmar e Registar Movimento", type="primary"):
          if not novo_lote_mov.strip():
            st.error("⚠️ Informe o número do lote.")
          elif "Recebimento" in tipo_op and data_val_mov < data_fab_mov:
            st.error(
                "⚠️ A data de validade não pode ser anterior à data de"
                " fabricação."
            )
          else:
            recarregar_estoque_fresco()
            df_est = st.session_state.estoque
            match_idx = df_est[df_est["Produto"] == produto_selecionado].index
            if len(match_idx) == 0:
              st.error("⚠️ Produto não encontrado ao atualizar o stock.")
              st.stop()

            idx = match_idx[0]
            setor_reg = df_est.loc[idx, "Setor"]
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            lote_limpo = novo_lote_mov.strip()

            if "Recebimento" in tipo_op:
              df_est.loc[idx, "Quantidade"] = int(
                  df_est.loc[idx, "Quantidade"]
              ) + int(qtd_op)
              df_est.loc[idx, "Lote"] = lote_limpo
              df_est.loc[idx, "Fabricacao"] = str(data_fab_mov)
              df_est.loc[idx, "Validade"] = str(data_val_mov)
              acao = "Recebimento"
            else:
              saldo_atual = int(df_est.loc[idx, "Quantidade"])
              if saldo_atual >= int(qtd_op):
                df_est.loc[idx, "Quantidade"] = saldo_atual - int(qtd_op)
                acao = "Expedição"
              else:
                st.error(
                    f"⚠️ Stock insuficiente! Disponível: {saldo_atual} un,"
                    f" Solicitado: {int(qtd_op)} un."
                )
                st.stop()

            df_est.loc[idx, "Ultima_Modificacao"] = data_atual
            df_est.loc[idx, "Modificado_Por"] = st.session_state.username

            nova_hist = pd.DataFrame(
                [[
                    data_atual,
                    st.session_state.username,
                    f"{acao} (Setor {setor_reg} - Lote {lote_limpo})",
                    produto_selecionado,
                    int(qtd_op),
                ]],
                columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
            )
            st.session_state.historico = pd.concat(
                [st.session_state.historico, nova_hist], ignore_index=True
            )

            salvar_estoque()
            salvar_historico()

            st.success(
                f"Operação de {acao} registada com sucesso no setor"
                f" **{setor_reg}**!"
            )
            if "codigo_lido_ativo" in st.session_state:
              del st.session_state["codigo_lido_ativo"]
            st.rerun()


# --- 3.1 GERAR ETIQUETAS DE CÓDIGOS DE BARRAS ---
elif menu == "🏷️ Gerar Etiquetas (Lotes)":
  st.markdown("## 🏷️ Módulo de Geração e Impressão de Etiquetas de Lotes")
  st.markdown(
      "Selecione um produto abaixo para gerar cartões de etiquetas prontos a"
      " imprimir para colar nas caixas ou produtos acabados."
  )

  if df.empty:
    st.info("Nenhum produto cadastrado.")
  else:
    prod_etq = st.selectbox(
        "Selecione o Produto para Etiqueta", df["Produto"].tolist()
    )
    qtd_etiquetas = st.number_input(
        "Número de Cópias de Etiquetas", min_value=1, max_value=100, value=5
    )

    row_prod = df[df["Produto"] == prod_etq].iloc[0]
    c_barras = row_prod["Codigo_Barras"]
    lote_prod = row_prod.get("Lote", "N/A")
    val_prod = row_prod.get("Validade", "N/A")
    setor_prod = row_prod["Setor"]

    st.markdown("---")
    st.subheader("👁️ Pré-visualização da Etiqueta Térmica")

    etiquetas_html = ""
    for _ in range(int(qtd_etiquetas)):
      etiquetas_html += f"""
            <div style="display: inline-block; width: 280px; border: 2px dashed #333; padding: 12px; margin: 8px; border-radius: 8px; font-family: monospace; background: white; color: black;">
                <h4 style="margin: 0 0 5px 0; text-align: center; font-size: 15px;">🍲 RBM ALIMENTOS</h4>
                <hr style="border: 0.5px solid #333;">
                <b>Prod:</b> {prod_etq}<br>
                <b>Setor:</b> {setor_prod}<br>
                <b>Lote:</b> {lote_prod} | <b>Val:</b> {val_prod}<br>
                <div style="text-align: center; margin-top: 8px; font-size: 20px; font-weight: bold; letter-spacing: 3px;">|||| | |||||| || |</div>
                <div style="text-align: center; font-size: 12px;">{c_barras}</div>
            </div>
            """

    st.markdown(etiquetas_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "💡 **Dica de Impressão:** Pode pressionar **Ctrl + P** no seu navegador"
        " para imprimir esta página diretamente numa impressora de etiquetas"
        " térmica ou comum."
    )


# --- 4. GESTÃO DE PEDIDOS & CHECK-LIST ---
elif menu == "📋 Gestão de Pedidos & Check-list":
  st.markdown("## 📋 Setor de Separação de Pedidos & Check-list")
  sub_tab1, sub_tab2 = st.tabs([
      "📸 Criar Novo Pedido (Importação / Manual)",
      "📦 Ver Pedidos Salvos & Ativos",
  ])

  with sub_tab1:
    with st.container(border=True):
      st.subheader("1. Capturar ou Inserir Dados do Pedido")
      tipo_cap = st.radio(
          "Origem do Pedido",
          ["Carregar Ficheiro de Talão", "Apenas Inserção Manual"],
          horizontal=True,
      )

      img_ped = None
      if tipo_cap == "Carregar Ficheiro de Talão":
        img_ped = st.file_uploader(
            "Ficheiro de imagem do talão", type=["png", "jpg", "jpeg"]
        )

      cli_nome = st.text_input(
          "Nome do Cliente / Destino",
          value="Neriah Comércio",
          placeholder="Ex: Neriah Comércio",
      )

      if "temp_itens" not in st.session_state:
        st.session_state.temp_itens = []

      st.markdown("---")
      st.info(
          "⚡ **Atalho de Importação:** Clique no botão abaixo para carregar"
          " automaticamente todos os 22 itens do talão da Neriah."
      )
      if st.button(
          "⚡ [Importação Automática] Carregar Itens do Talão da Neriah",
          type="primary",
      ):
        itens_talao_neriah = [
            {"produto": "Chocolate - Calzone 12 Uni", "qtd": 1},
            {
                "produto": "Duo - Chocolate Branco e Preto 12 Uni",
                "qtd": 1,
            },
            {"produto": "Nutella - Calzone 12 Uni", "qtd": 1},
            {"produto": "Bolonhesa - Calzone 12 Uni", "qtd": 1},
            {"produto": "Português - Calzone 12 Uni", "qtd": 3},
            {"produto": "Frango Supremo - Calzone 12 Uni", "qtd": 2},
            {"produto": "Frango Catupiry - Calzone 12 Uni", "qtd": 4},
            {"produto": "Quatro Queijos - Calzone 12 Uni", "qtd": 2},
            {"produto": "Frango c/ Muçarela e Orégano - Calzone", "qtd": 3},
            {"produto": "Calabresa - Calzone 12 Uni", "qtd": 2},
            {"produto": "Calab c/Mussarela - Calzone 12 Uni", "qtd": 4},
            {"produto": "Filé Quatro Queijos - Calzone 12 Uni", "qtd": 3},
            {"produto": "Carne Seca - Calzone 12 Uni", "qtd": 1},
            {"produto": "Filé c/ Cheddar - Calzone 12 Uni", "qtd": 2},
            {"produto": "Pizza Calabresa - 4 Unidades", "qtd": 2},
            {"produto": "Pizza Portuguesa - 4 Unidades", "qtd": 1},
            {"produto": "Pizza de Bacon com Catupiry - 4 Unidades", "qtd": 1},
            {"produto": "Recheio Camarão Premium 800g", "qtd": 1},
            {"produto": "Recheio Carne 800g", "qtd": 2},
            {"produto": "Recheio de Mussarela 800g", "qtd": 3},
            {"produto": "Recheio Calabresa 0,8 Kg", "qtd": 1},
            {"produto": "Massa p/ Pastel (2 Unidades)", "qtd": 1},
        ]
        st.session_state.temp_itens = itens_talao_neriah
        st.success("⚡ Todos os itens do talão foram carregados com sucesso!")
        st.rerun()

      st.markdown("---")
      st.subheader("2. Adicionar ou Ajustar Itens do Pedido")

      modo_add_ped = st.radio(
          "Como adicionar o item?",
          ["Selecionar do Stock", "Digitar Nome Manualmente"],
          horizontal=True,
          key="modo_add_pedido",
      )

      c_p1, c_p2 = st.columns([2, 1])
      with c_p1:
        if modo_add_ped == "Selecionar do Stock" and not df.empty:
          item_sel = st.selectbox(
              "Produto do Stock", df["Produto"].tolist(), key="sel_item_ped"
          )
        else:
          item_sel = st.text_input(
              "Nome do Produto Manual / Personalizado",
              key="txt_item_ped_manual",
          )
      with c_p2:
        qtd_sel = st.number_input(
            "Quantidade", min_value=1, value=1, key="qtd_item_ped"
        )

      if st.button("➕ Adicionar Item à Lista do Pedido"):
        if item_sel and str(item_sel).strip():
          st.session_state.temp_itens.append(
              {"produto": str(item_sel).strip(), "qtd": int(qtd_sel)}
          )
          st.success(f"Adicionado: {item_sel} ({int(qtd_sel)} un)")
        else:
          st.error("Informe o nome do produto.")

      if st.session_state.temp_itens:
        st.markdown("#### **Itens Adicionados no Pedido Atual:**")
        for idx_t, it in enumerate(st.session_state.temp_itens):
          col_t1, col_t2 = st.columns([4, 1])
          with col_t1:
            st.write(f"- {it['produto']}: **{it['qtd']} un**")
          with col_t2:
            if st.button("✖", key=f"rm_temp_{idx_t}"):
              st.session_state.temp_itens.pop(idx_t)
              st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🚀 Gerar Pedido e Abrir Janela de Separação", type="primary"
        ):
          if cli_nome and cli_nome.strip():
            pid = f"Pedido_{datetime.datetime.now().strftime('%H%M%S')}"
            st.session_state.pedidos_ativos[pid] = {
                "cliente": cli_nome.strip(),
                "data_criacao": datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "itens": [
                    {
                        "produto": i["produto"],
                        "qtd_pedida": int(i["qtd"]),
                        "qtd_separada": 0,
                    }
                    for i in st.session_state.temp_itens
                ],
                "concluido": False,
            }
            st.session_state.temp_itens = []
            st.success(
                f"🎉 Pedido '{pid}' gerado com sucesso! Vá para a aba 'Ver"
                " Pedidos Salvos & Ativos' para iniciar a separação."
            )
            st.rerun()
          else:
            st.error("Por favor, preencha o nome do cliente/destino.")

  with sub_tab2:
    st.subheader("📦 Lista de Todos os Pedidos Salvos e Ativos")
    if not st.session_state.pedidos_ativos:
      st.info("Nenhum pedido registado ou em separação no momento.")
    else:

      def executar_baixa_pedido(pid_alvo, dados_pedido):
        if dados_pedido.get("concluido"):
          return True
        recarregar_estoque_fresco()
        df_est = st.session_state.estoque
        erro_stk = False
        itens_para_abater = []

        for item in dados_pedido["itens"]:
          p_n = item["produto"]
          q_s = int(item["qtd_pedida"])
          match_stk = df_est[df_est["Produto"] == p_n]
          if match_stk.empty:
            erro_stk = True
            st.error(
                f"⚠️ Produto '{p_n}' não encontrado no stock para dar baixa."
            )
          else:
            r_idx = match_stk.index[0]
            saldo = int(df_est.loc[r_idx, "Quantidade"])
            if saldo >= q_s:
              itens_para_abater.append(
                  (r_idx, p_n, q_s, df_est.loc[r_idx, "Setor"])
              )
            else:
              erro_stk = True
              st.error(
                  f"⚠️ Stock insuficiente para **{p_n}** no setor"
                  f" {df_est.loc[r_idx, 'Setor']} (Disponível: {saldo},"
                  f" Pedido: {q_s})!"
              )

        if not erro_stk:
          data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
          for r_idx, p_n, q_s, setor_prod in itens_para_abater:
            df_est.loc[r_idx, "Quantidade"] = (
                int(df_est.loc[r_idx, "Quantidade"]) - q_s
            )
            df_est.loc[r_idx, "Ultima_Modificacao"] = data_atual
            df_est.loc[r_idx, "Modificado_Por"] = st.session_state.username

            nova_hist = pd.DataFrame(
                [[
                    data_atual,
                    st.session_state.username,
                    f"Expedição Setor {setor_prod} ({pid_alvo})",
                    p_n,
                    q_s,
                ]],
                columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
            )
            st.session_state.historico = pd.concat(
                [st.session_state.historico, nova_hist], ignore_index=True
            )

          salvar_estoque()
          salvar_historico()
          dados_pedido["concluido"] = True
          return True
        return False

      for pid, pdata in st.session_state.pedidos_ativos.items():
        status_txt = (
            "✅ Concluído (Baixa por Setor Efetuada)"
            if pdata["concluido"]
            else "⏳ Em Andamento (Separação)"
        )
        data_criacao = pdata.get("data_criacao", "Data não registada")

        with st.expander(
            f"📦 {pid} — Cliente: **{pdata['cliente']}** [{status_txt}]"
            f" (Criado em: {data_criacao})",
            expanded=not pdata["concluido"],
        ):
          modo_baixa = "Manual (confirmar por botão no final)"
          if not pdata["concluido"]:
            modo_baixa = st.radio(
                "⚙️ Modo de Baixa no Stock:",
                [
                    "Automática (ao concluir 100% da separação)",
                    "Manual (confirmar por botão no final)",
                ],
                key=f"modo_baixa_{pid}",
                horizontal=True,
            )

            scan_codigo = st.text_input(
                f"🔍 Código de Barras / Leitor ({pid})",
                key=f"input_sep_codigo_{pid}",
                placeholder="Passe o leitor ou digite...",
            ).strip()
            if scan_codigo:
              match_bar = df[
                  df["Codigo_Barras"].astype(str).str.strip() == scan_codigo
              ]
              if not match_bar.empty:
                nome_prod_encontrado = match_bar.iloc[0]["Produto"]
                setor_encontrado = match_bar.iloc[0]["Setor"]
                achou_no_pedido = False
                for itm in pdata["itens"]:
                  if itm["produto"] == nome_prod_encontrado:
                    achou_no_pedido = True
                    if itm["qtd_separada"] < itm["qtd_pedida"]:
                      itm["qtd_separada"] += 1
                      st.toast(
                          f"✔️ Separado 1 {nome_prod_encontrado} [Setor:"
                          f" {setor_encontrado}]"
                          f" ({itm['qtd_separada']}/{itm['qtd_pedida']})"
                      )
                    else:
                      st.warning(
                          f"O item {nome_prod_encontrado} já está completo neste"
                          " pedido!"
                      )
                if not achou_no_pedido:
                  st.error(
                      f"O produto '{nome_prod_encontrado}' (Setor:"
                      f" {setor_encontrado}) não pertence a este pedido!"
                  )
              else:
                st.error("⚠️ Código de barras desconhecido no sistema!")

          st.markdown("---")
          todos_ok = True
          for i_idx, item in enumerate(pdata["itens"]):
            p_name = item["produto"]
            m_qtd = int(item["qtd_pedida"])
            a_qtd = int(item["qtd_separada"])

            match_stk = df[df["Produto"] == p_name]
            setor_item = (
                match_stk.iloc[0]["Setor"]
                if not match_stk.empty
                else "Manual/Outros"
            )

            estilo_cor = (
                "color: #28a745; font-weight: bold; background-color: #e8f5e9;"
                " padding: 4px 8px; border-radius: 4px;"
                if a_qtd >= m_qtd
                else "color: #333;"
            )

            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
              st.markdown(
                  f"<span style='{estilo_cor}'>📦 {p_name}<br><small>🏭 Setor:"
                  f" <b>{setor_item}</b></small></span>",
                  unsafe_allow_html=True,
              )
            with col2:
              st.markdown(
                  f"<span style='{estilo_cor}'>Separado:"
                  f" **{a_qtd}/{m_qtd}**</span>",
                  unsafe_allow_html=True,
              )
            with col3:
              if not pdata["concluido"]:
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                  if st.button("➕", key=f"mais_{pid}_{i_idx}"):
                    if a_qtd < m_qtd:
                      item["qtd_separada"] += 1
                      st.rerun()
                with b_col2:
                  if st.button("➖", key=f"menos_{pid}_{i_idx}"):
                    if a_qtd > 0:
                      item["qtd_separada"] -= 1
                      st.rerun()

            if a_qtd < m_qtd:
              todos_ok = False

          st.markdown("<br>", unsafe_allow_html=True)

          if pdata["concluido"]:
            st.success("✅ **Pedido Finalizado e Baixado nos Setores!**")
          elif not todos_ok:
            st.warning("⚠️ Separação em andamento.")
          else:
            if "Automática" in modo_baixa:
              sucesso = executar_baixa_pedido(pid, pdata)
              if sucesso:
                st.success("⚡ **Baixa Automática Concluída!**")
                st.rerun()
            else:
              if st.button(
                  f"📥 Confirmar e Dar Baixa Manual ({pid})",
                  key=f"baixar_{pid}",
                  type="primary",
              ):
                sucesso = executar_baixa_pedido(pid, pdata)
                if sucesso:
                  st.success("✅ Baixa efetuada!")
                  st.rerun()


# --- 5. GESTÃO DE CLIENTES & PEDIDOS ---
elif menu == "👥 Gestão de Clientes & Pedidos":
  st.markdown("## 👥 Gestão de Clientes & Controlo de Pedidos")
  tab_cli1, tab_cli2, tab_cli3 = st.tabs([
      "🏢 Cadastrar & Listar Clientes",
      "📦 Controlo de Pedidos dos Clientes",
      "📊 Relatório Mensal por Cliente",
  ])

  with tab_cli1:
    with st.container(border=True):
      st.subheader("➕ Registar Novo Cliente")
      c_razao = st.text_input("Razão Social").strip()
      c_fantasia = st.text_input("Nome Fantasia").strip()
      c_cnpj = st.text_input("CNPJ", placeholder="00.000.000/0001-00").strip()
      c_end = st.text_area("Endereço Completo").strip()
      c_cont = st.text_input("Contacto (Telefone / E-mail)").strip()

      if st.button("💾 Guardar Novo Cliente", type="primary"):
        if c_razao and c_cnpj:
          cnpj_existente = any(
              str(c.get("cnpj", "")).strip() == c_cnpj
              for c in st.session_state.clientes
          )
          if cnpj_existente:
            st.error("⚠️ Já existe um cliente registado com este CNPJ.")
          else:
            novo_c = {
                "razao_social": c_razao,
                "nome_fantasia": c_fantasia if c_fantasia else c_razao,
                "cnpj": c_cnpj,
                "endereco": c_end,
                "contacto": c_cont,
            }
            st.session_state.clientes.append(novo_c)
            salvar_clientes()
            st.success(f"Cliente '{c_razao}' registado com sucesso!")
            st.rerun()
        else:
          st.error("Preencha a Razão Social e o CNPJ.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📋 Lista de Clientes Registados")
    if not st.session_state.clientes:
      st.info("Nenhum cliente registado.")
    else:
      for idx, cli in enumerate(st.session_state.clientes):
        with st.container(border=True):
          col_a, col_b = st.columns([3, 1])
          with col_a:
            st.write(
                f"🏢 **{cli['razao_social']}** (Fantasia:"
                f" *{cli['nome_fantasia']}*)"
            )
            st.caption(
                f"CNPJ: {cli['cnpj']} | Endereço: {cli['endereco']} |"
                f" Contacto: {cli['contacto']}"
            )
          with col_b:
            if st.button("🗑️ Eliminar", key=f"del_cli_{idx}"):
              st.session_state.clientes.pop(idx)
              salvar_clientes()
              st.success("Cliente eliminado!")
              st.rerun()

  with tab_cli2:
    with st.container(border=True):
      st.subheader("📦 Registar Pedido para Cliente")
      if not st.session_state.clientes:
        st.warning("⚠️ Cadastre um cliente primeiro.")
      elif df.empty:
        st.warning("⚠️ Cadastre um produto no stock primeiro.")
      else:
        lista_nomes_clientes = [
            c["razao_social"] for c in st.session_state.clientes
        ]
        sel_cliente_ped = st.selectbox(
            "Selecione o Cliente", lista_nomes_clientes
        )
        data_pedido_cli = st.date_input(
            "Data do Pedido", datetime.date.today(), key="dt_ped_cli"
        )

        if "itens_cli_temp" not in st.session_state:
          st.session_state.itens_cli_temp = []

        st.markdown("---")
        col_ip1, col_ip2 = st.columns([2, 1])
        with col_ip1:
          prod_escolhido = st.selectbox(
              "Produto do Stock", df["Produto"].tolist(), key="sel_p_cli"
          )
        with col_ip2:
          qtd_escolhida = st.number_input(
              "Quantidade", min_value=1, value=1, key="q_p_cli"
          )

        if st.button("➕ Adicionar Item ao Pedido do Cliente"):
          st.session_state.itens_cli_temp.append(
              {"produto": prod_escolhido, "quantidade": int(qtd_escolhida)}
          )
          st.success(f"Adicionado: {prod_escolhido} ({int(qtd_escolhida)} un)")

        if st.session_state.itens_cli_temp:
          st.markdown("**Itens no Pedido:**")
          for it in st.session_state.itens_cli_temp:
            st.write(f"- {it['produto']}: **{it['quantidade']} un**")

          if st.button(
              "🚀 Finalizar e Registar Pedido do Cliente", type="primary"
          ):
            num_ped_cli = (
                f"PC_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            novo_reg_ped = {
                "id_pedido": num_ped_cli,
                "cliente": sel_cliente_ped,
                "data": str(data_pedido_cli),
                "mes_ano": data_pedido_cli.strftime("%Y-%m"),
                "itens": st.session_state.itens_cli_temp,
                "status": "Registado / Em Separação",
            }
            st.session_state.clientes_pedidos.append(novo_reg_ped)
            salvar_clientes_pedidos()
            st.session_state.itens_cli_temp = []
            st.success(f"🎉 Pedido '{num_ped_cli}' registado com sucesso!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📦 Histórico de Pedidos de Clientes")
    if not st.session_state.clientes_pedidos:
      st.info("Nenhum pedido de cliente registado.")
    else:
      for cp in st.session_state.clientes_pedidos:
        with st.container(border=True):
          st.write(
              f"📦 **{cp['id_pedido']}** — Cliente: **{cp['cliente']}** | Data:"
              f" {cp['data']} | Status: *{cp['status']}*"
          )
          for i in cp["itens"]:
            st.caption(
                f"&nbsp;&nbsp;&nbsp;&nbsp;• {i['produto']}: {i['quantidade']}"
                " un"
            )

  with tab_cli3:
    with st.container(border=True):
      st.subheader("📊 Relatório Mensal de Pedidos por Cliente")
      if not st.session_state.clientes:
        st.info("Nenhum cliente registado.")
      else:
        lista_nomes_clientes = [
            c["razao_social"] for c in st.session_state.clientes
        ]
        filtro_cli_rel = st.selectbox(
            "Selecionar Cliente", lista_nomes_clientes, key="rel_cli_sel"
        )
        mes_atual_str = datetime.date.today().strftime("%Y-%m")
        filtro_mes = st.text_input(
            "Filtrar por Mês e Ano (AAAA-MM)", value=mes_atual_str
        ).strip()

        pedidos_filtrados = [
            p
            for p in st.session_state.clientes_pedidos
            if p["cliente"] == filtro_cli_rel
            and p.get("mes_ano", str(p["data"])[:7]) == filtro_mes
        ]

        st.markdown(
            f"### Relatório para **{filtro_cli_rel}** no período:"
            f" **{filtro_mes}**"
        )
        st.write(f"Total de pedidos no mês: **{len(pedidos_filtrados)}**")

        if pedidos_filtrados:
          dados_tabela = []
          for ped in pedidos_filtrados:
            for itm in ped["itens"]:
              dados_tabela.append({
                  "ID Pedido": ped["id_pedido"],
                  "Data": ped["data"],
                  "Produto": itm["produto"],
                  "Quantidade": itm["quantidade"],
                  "Status": ped["status"],
              })

          df_rel = pd.DataFrame(dados_tabela)
          st.dataframe(df_rel, use_container_width=True)

          csv_rel = df_rel.to_csv(index=False).encode("utf-8-sig")
          st.download_button(
              label=(
                  f"📥 Descarregar Relatório de {filtro_cli_rel}"
                  f" ({filtro_mes}) em CSV"
              ),
              data=csv_rel,
              file_name=(
                  f"relatorio_cliente_{filtro_cli_rel}_{filtro_mes}.csv"
              ),
              mime="text/csv",
          )
        else:
          st.info("Nenhum pedido encontrado para este cliente no mês selecionado.")


# --- 6. MENSAGENS (TEMPO REAL) ---
elif menu.startswith("💬 Mensagens"):
  st.markdown("## 💬 Central de Mensagens & Bate-Papo Interno")

  recarregar_mensagens_frescas()

  utilizadores_disponiveis = [
      u
      for u in st.session_state.users.keys()
      if u != st.session_state.username
  ]

  if not utilizadores_disponiveis:
    st.info("ℹ️ Não existem outros utilizadores registados.")
  else:
    destinatario = st.selectbox(
        "👥 Selecione o Utilizador para Conversar", utilizadores_disponiveis
    )

    st.markdown("---")
    st.markdown(f"### 💬 Conversa com: **{destinatario}**")

    def renderizar_conversa(user_atual, outro_user):
      recarregar_mensagens_frescas()

      alterado = False
      for m in st.session_state.mensagens:
        if (
            m["para"] == user_atual
            and m["de"] == outro_user
            and not m.get("lida", False)
        ):
          m["lida"] = True
          alterado = True
      if alterado:
        salvar_mensagens()

      conversa = [
          m
          for m in st.session_state.mensagens
          if (
              (m["de"] == user_atual and m["para"] == outro_user)
              or (m["de"] == outro_user and m["para"] == user_atual)
          )
      ]

      chat_container = st.container(height=350)
      with chat_container:
        if not conversa:
          st.info(f"Sem mensagens ainda com **{outro_user}**.")
        else:
          for msg in conversa:
            remetente = msg["de"]
            texto = msg["texto"]
            data_envio = msg["data"]
            ficheiro_info = msg.get("ficheiro", None)

            if remetente == user_atual:
              st.markdown(
                  f"<div style='text-align: right; background-color: #d1e7dd; color: #111; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%;'>"
                  f"<small><b>Você</b> — {data_envio}</small><br>{texto}</div>",
                  unsafe_allow_html=True,
              )
              if ficheiro_info:
                st.markdown(
                    f"<div style='text-align: right;'><a"
                    f" href='data:application/octet-stream;base64,{ficheiro_info['dados']}'"
                    f" download='{ficheiro_info['nome']}'>📎 Ficheiro"
                    f" Anexado: {ficheiro_info['nome']}</a></div>",
                    unsafe_allow_html=True,
                )
            else:
              st.markdown(
                  f"<div style='text-align: left; background-color: #f8d7da; color: #111; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;'>"
                  f"<small><b>{remetente}</b> — {data_envio}</small><br>{texto}</div>",
                  unsafe_allow_html=True,
              )
              if ficheiro_info:
                st.markdown(
                    f"<div style='text-align: left;'><a"
                    f" href='data:application/octet-stream;base64,{ficheiro_info['dados']}'"
                    f" download='{ficheiro_info['nome']}'>📎 Ficheiro"
                    f" Anexado: {ficheiro_info['nome']}</a></div>",
                    unsafe_allow_html=True,
                )

    if hasattr(st, "fragment"):

      @st.fragment(run_every="3s")
      def chat_ao_vivo():
        renderizar_conversa(st.session_state.username, destinatario)

      chat_ao_vivo()
    else:
      renderizar_conversa(st.session_state.username, destinatario)
      if st.button("🔄 Atualizar Mensagens Agora"):
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.form(key="form_envio_msg", clear_on_submit=True):
      texto_msg = st.text_area(
          "Escreva a sua mensagem...", placeholder="Digite aqui..."
      )
      anexo_arquivo = st.file_uploader(
          "📎 Anexar Ficheiro", type=["png", "jpg", "jpeg", "pdf", "csv", "txt"]
      )
      btn_enviar = st.form_submit_button("🚀 Enviar Mensagem", type="primary")

      if btn_enviar:
        if texto_msg.strip() or anexo_arquivo:
          d_arquivo = None
          if anexo_arquivo is not None:
            bytes_arq = anexo_arquivo.read()
            b64_arq = base64.b64encode(bytes_arq).decode("utf-8")
            d_arquivo = {"nome": anexo_arquivo.name, "dados": b64_arq}

          recarregar_mensagens_frescas()

          nova_msg = {
              "de": st.session_state.username,
              "para": destinatario,
              "texto": (
                  texto_msg.strip() if texto_msg.strip() else "[Ficheiro Anexado]"
              ),
              "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
              "lida": False,
              "ficheiro": d_arquivo,
          }
          st.session_state.mensagens.append(nova_msg)
          salvar_mensagens()
          st.success("Mensagem enviada!")
          st.rerun()
        else:
          st.error("Escreva uma mensagem ou anexe um ficheiro.")


# --- 7. RELATÓRIOS & ROMANEIOS ---
elif menu == "📊 Romaneios & Relatórios":
  st.markdown("## 📊 Romaneios & Relatórios por Período")
  st.markdown(
      "Selecione o tipo de relatório e o intervalo de datas desejado para gerar"
      " um romaneio organizado."
  )

  tipo_relatorio = st.selectbox(
      "Tipo de Relatório",
      [
          "Histórico de Movimentações / Expedição (por Data)",
          "Pedidos de Clientes (por Data)",
          "Posição Atual do Stock (Geral / Setor)",
      ],
  )

  col_dt1, col_dt2 = st.columns(2)
  with col_dt1:
    data_inicio = st.date_input(
        "Data Inicial", value=datetime.date.today().replace(day=1)
    )
  with col_dt2:
    data_fim = st.date_input("Data Final", value=datetime.date.today())

  if data_inicio > data_fim:
    st.error("⚠️ A Data Inicial não pode ser maior que a Data Final.")
  else:
    dt_ini_str = data_inicio.strftime("%Y-%m-%d")
    dt_fim_str = data_fim.strftime("%Y-%m-%d")

    df_relatorio = pd.DataFrame()
    titulo_rel = tipo_relatorio

    if tipo_relatorio == "Histórico de Movimentações / Expedição (por Data)":
      hist_df = st.session_state.historico.copy()
      if not hist_df.empty and "Data" in hist_df.columns:
        hist_df["_data_apenas"] = hist_df["Data"].astype(str).str.slice(0, 10)
        df_relatorio = hist_df[
            (hist_df["_data_apenas"] >= dt_ini_str)
            & (hist_df["_data_apenas"] <= dt_fim_str)
        ].drop(columns=["_data_apenas"])

    elif tipo_relatorio == "Pedidos de Clientes (por Data)":
      linhas_ped = []
      for ped in st.session_state.clientes_pedidos:
        p_data = str(ped.get("data", ""))[:10]
        if dt_ini_str <= p_data <= dt_fim_str:
          for itm in ped.get("itens", []):
            linhas_ped.append({
                "ID Pedido": ped.get("id_pedido", ""),
                "Data": ped.get("data", ""),
                "Cliente": ped.get("cliente", ""),
                "Produto": itm.get("produto", ""),
                "Quantidade": itm.get("quantidade", 0),
                "Status": ped.get("status", ""),
            })
      df_relatorio = pd.DataFrame(linhas_ped)

    else:
      setor_rel = st.selectbox(
          "Filtrar Stock por Setor",
          ["Todos os Setores"] + st.session_state.setores,
          key="rel_stk_setor",
      )
      stk_df = df.copy()
      if setor_rel != "Todos os Setores":
        stk_df = stk_df[stk_df["Setor"] == setor_rel]
      colunas_uteis = [
          c
          for c in [
              "Codigo_Barras",
              "Produto",
              "Setor",
              "Lote",
              "Quantidade",
              "Limite_Minimo",
              "Validade",
              "Ultima_Modificacao",
          ]
          if c in stk_df.columns
      ]
      df_relatorio = stk_df[colunas_uteis]

    st.markdown("---")

    if df_relatorio.empty:
      st.info(
          f"ℹ️ Nenhum registo encontrado entre **{dt_ini_str}** e"
          f" **{dt_fim_str}**."
      )
    else:
      st.subheader("📋 Pré-visualização Organizada do Romaneio")
      st.dataframe(df_relatorio, use_container_width=True)

      linhas_html = ""
      for _, linha in df_relatorio.iterrows():
        celulas = "".join([
            f"<td style='padding: 8px; border: 1px solid #ccc;'>{val}</td>"
            for val in linha.values
        ])
        linhas_html += f"<tr>{celulas}</tr>"

      cabecalhos_html = "".join([
          f"<th style='padding: 8px; border: 1px solid #ccc; background-color: #2c3e50; color: white; text-align: left;'>{col}</th>"
          for col in df_relatorio.columns
      ])

      romaneio_html = f"""
            <div id="romaneio-print" style="background: white; color: #222; padding: 24px; border-radius: 10px; border: 1px solid #ddd; font-family: Arial, sans-serif;">
                <div style="display: flex; justify-content: space-between; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 15px;">
                    <div>
                        <h3 style="margin: 0; color: #2c3e50;">🍲 RBM ALIMENTOS — ROMANEIO / RELATÓRIO</h3>
                        <p style="margin: 4px 0 0 0; font-size: 13px; color: #555;"><b>Tipo:</b> {titulo_rel}</p>
                    </div>
                    <div style="text-align: right; font-size: 13px; color: #555;">
                        <b>Período:</b> {dt_ini_str} a {dt_fim_str}<br>
                        <b>Gerado em:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}<br>
                        <b>Total de linhas:</b> {len(df_relatorio)}
                    </div>
                </div>
                <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead><tr>{cabecalhos_html}</tr></thead>
                    <tbody>{linhas_html}</tbody>
                </table>
            </div>
            """

      st.markdown("### 🖨️ Romaneio Formatado (Pronto para Imprimir / PDF)")
      st.markdown(romaneio_html, unsafe_allow_html=True)

      st.markdown("<br>", unsafe_allow_html=True)
      c_exp1, c_exp2 = st.columns(2)

      with c_exp1:
        csv_limpo = df_relatorio.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Baixar Planilha Organizada (CSV UTF-8)",
            data=csv_limpo,
            file_name=f"romaneio_{dt_ini_str}_a_{dt_fim_str}.csv",
            mime="text/csv",
            use_container_width=True,
        )

      with c_exp2:
        html_completo = f"""
                <!DOCTYPE html>
                <html>
                <head><meta charset="utf-8"><title>Romaneio RBM Alimentos</title></head>
                <body style="margin: 20px;">{romaneio_html}</body>
                </html>
                """.encode("utf-8")
        st.download_button(
            label="📄 Baixar Romaneio Formatado (HTML / PDF)",
            data=html_completo,
            file_name=f"romaneio_{dt_ini_str}_a_{dt_fim_str}.html",
            mime="text/html",
            use_container_width=True,
        )

      st.caption(
          "💡 Dica: Ao abrir o ficheiro HTML formatado no navegador, basta"
          " usar Imprimir (Ctrl+P) e escolher 'Salvar como PDF' para ter um"
          " documento visualmente limpo."
      )


# --- 8. HISTÓRICO ---
elif menu == "📜 Histórico de Auditoria":
  st.markdown("## 📜 Histórico de Atividades")
  st.dataframe(st.session_state.historico, use_container_width=True)
