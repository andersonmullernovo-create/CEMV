import datetime
import json
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Configuração da página orientada ao setor alimentício
st.set_page_config(
    page_title="Gestão de Stock - RBM Alimentos",
    page_icon="🍲",
    layout="wide",
)

# --- FICHEIROS DE PERSISTÊNCIA LOCAL ---
ARQ_ESTOQUE = "estoque_rbm_dados.csv"
ARQ_SETORES = "setores_rbm_dados.json"
ARQ_USERS = "users_rbm_dados.json"
ARQ_HIST = "historico_rbm_dados.csv"
ARQ_CONFIG = "config_visual_dados.json"
ARQ_MENSAGENS = "mensagens_rbm_dados.json"

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


def salvar_estoque():
  st.session_state.estoque.to_csv(ARQ_ESTOQUE, index=False)


def salvar_setores():
  with open(ARQ_SETORES, "w", encoding="utf-8") as f:
    json.dump(st.session_state.setores, f, ensure_ascii=False)


def salvar_users():
  with open(ARQ_USERS, "w", encoding="utf-8") as f:
    json.dump(st.session_state.users, f, ensure_ascii=False)


def salvar_historico():
  st.session_state.historico.to_csv(ARQ_HIST, index=False)


def salvar_config():
  with open(ARQ_CONFIG, "w", encoding="utf-8") as f:
    json.dump(st.session_state.config_visual, f, ensure_ascii=False)


def salvar_mensagens():
  with open(ARQ_MENSAGENS, "w", encoding="utf-8") as f:
    json.dump(st.session_state.mensagens, f, ensure_ascii=False)


# --- INICIALIZAÇÃO COM CARREGAMENTO PERSISTENTE ---
if "users" not in st.session_state:
  if os.path.exists(ARQ_USERS):
    with open(ARQ_USERS, "r", encoding="utf-8") as f:
      st.session_state.users = json.load(f)
  else:
    st.session_state.users = {
        "admin": {
            "senha": "1234",
            "perfil": "Administrador",
            "pode_cadastrar": True,
            "pode_excluir": True,
            "pode_movimentar": True,
        },
        "operador": {
            "senha": "abcd",
            "perfil": "Operador",
            "pode_cadastrar": False,
            "pode_excluir": False,
            "pode_movimentar": True,
        },
    }
    salvar_users()

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.perfil = ""

if "config_visual" not in st.session_state:
  if os.path.exists(ARQ_CONFIG):
    with open(ARQ_CONFIG, "r", encoding="utf-8") as f:
      st.session_state.config_visual = json.load(f)
  else:
    st.session_state.config_visual = {
        "tamanho_fonte": "16px",
        "cor_fundo_tabela": "#f9f9f9",
        "cor_texto": "#31333F",
        "fundo_app": "Gradiente Azul Moderno",
        "fundo_login": "Gradiente Azul Moderno",
    }
    salvar_config()

if "historico" not in st.session_state:
  if os.path.exists(ARQ_HIST):
    st.session_state.historico = pd.read_csv(ARQ_HIST)
  else:
    st.session_state.historico = pd.DataFrame(
        columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"]
    )
    salvar_historico()

if "mensagens" not in st.session_state:
  if os.path.exists(ARQ_MENSAGENS):
    with open(ARQ_MENSAGENS, "r", encoding="utf-8") as f:
      st.session_state.mensagens = json.load(f)
  else:
    st.session_state.mensagens = []
    salvar_mensagens()

if "agenda_eventos" not in st.session_state:
  st.session_state.agenda_eventos = []

if "setores" not in st.session_state:
  if os.path.exists(ARQ_SETORES):
    with open(ARQ_SETORES, "r", encoding="utf-8") as f:
      st.session_state.setores = json.load(f)
  else:
    st.session_state.setores = [
        "Armazém Central",
        "Câmara Fria",
        "Secos e Molhados",
    ]
    salvar_setores()

if "pedidos_ativos" not in st.session_state:
  st.session_state.pedidos_ativos = {}

if "estoque" not in st.session_state:
  if os.path.exists(ARQ_ESTOQUE):
    st.session_state.estoque = pd.read_csv(ARQ_ESTOQUE)
  else:
    st.session_state.estoque = pd.DataFrame({
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
        "Fabricacao": ["2026-10-01", "2026-09-15", "2026-10-10"],
        "Validade": ["2026-11-15", "2027-05-20", "2026-11-10"],
        "Ultima_Modificacao": ["2026-11-01", "2026-11-05", "2026-11-10"],
        "Modificado_Por": ["admin", "operador", "admin"],
    })
    salvar_estoque()

# Capturar código vindo do leitor ótico da câmara em tempo real
if "scanned_code" in st.query_params:
  st.session_state["codigo_lido_ativo"] = st.query_params["scanned_code"]
  st.query_params.clear()
  st.rerun()

cfg = st.session_state.config_visual
bg_css = TEMAS_FUNDO.get(
    cfg.get("fundo_app", "Gradiente Azul Moderno"), TEMAS_FUNDO["Gradiente Azul Moderno"]
)

st.markdown(
    f"""
    <style>
    * {{
        -webkit-touch-callout: none !important;
        -webkit-user-select: none !important;
        user-select: none !important;
    }}
    input, textarea, select {{
        -webkit-user-select: text !important;
        user-select: text !important;
    }}
    html, body, [class*="css"] {{
        font-size: {cfg.get('tamanho_fonte', '16px')} !important;
        color: {cfg.get('cor_texto', '#31333F')} !important;
    }}
    .stApp {{
        background: {bg_css};
        background-attachment: fixed;
    }}
    .stDataFrame {{
        background-color: {cfg.get('cor_fundo_tabela', '#f9f9f9')} !important;
    }}
    div[data-testid="stVerticalBlock"] > div[style*="border-color"] {{
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

      user_input = st.text_input("👤 Utilizador", key="login_user")
      pass_input = st.text_input(
          "🔑 Senha de Acesso", type="password", key="login_pass"
      )

      st.markdown("<br>", unsafe_allow_html=True)
      if st.button(
          "🚀 Entrar no Sistema", type="primary", use_container_width=True
      ):
        if (
            user_input in st.session_state.users
            and st.session_state.users[user_input]["senha"] == pass_input
        ):
          st.session_state.logged_in = True
          st.session_state.username = user_input
          st.session_state.perfil = st.session_state.users[user_input]["perfil"]
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
    "📋 Gestão de Pedidos & Check-list",
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
      novo_user = st.text_input("Nome do Utilizador")
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
              "senha": nova_senha,
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
        if desc_evento:
          st.session_state.agenda_eventos.append(
              {"data": str(data_evento), "evento": desc_evento}
          )
          st.success("Adicionado!")
    st.markdown("<br>", unsafe_allow_html=True)
    for ev in st.session_state.agenda_eventos:
      st.write(f"📅 **{ev['data']}**: {ev['evento']}")

  with tab_adm4:
    with st.container(border=True):
      st.subheader("✏️ Edição Rápida de Itens Cadastrados")
      prod_editar = st.selectbox(
          "Selecione o produto", df["Produto"].tolist(), key="sel_ed"
      )
      if prod_editar:
        idx_ed = df[df["Produto"] == prod_editar].index[0]
        nn = st.text_input("Nome", value=df.loc[idx_ed, "Produto"], key="ed_n")
        nd = st.text_area(
            "Descrição", value=df.loc[idx_ed, "Descricao"], key="ed_d"
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
          df.loc[idx_ed, "Produto"] = nn
          df.loc[idx_ed, "Descricao"] = nd
          df.loc[idx_ed, "Unidades_Embalagem"] = ne
          df.loc[idx_ed, "Limite_Minimo"] = nm
          df.loc[idx_ed, "Setor"] = ns
          salvar_estoque()
          st.success("Atualizado e guardado com sucesso!")
          st.rerun()

  with tab_adm5:
    with st.container(border=True):
      st.subheader("💾 Backup e Restauro de Dados")
      csv_data = df.to_csv(index=False).encode("utf-8")
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
            st.session_state.estoque = df_restaurado
            salvar_estoque()
            st.success("Stock restaurado com sucesso!")
            st.rerun()
          except Exception as e:
            st.error(f"Erro ao ler o ficheiro: {e}")

  with tab_adm6:
    with st.container(border=True):
      st.subheader("🎨 Estilo & Eliminação de Produtos")
      prod_ex = st.selectbox(
          "Eliminar Produto do Catálogo", df["Produto"].tolist(), key="ex_p"
      )
      if st.button("Confirmar Eliminação"):
        st.session_state.estoque = df[
            df["Produto"] != prod_ex
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
        st.session_state.config_visual["tamanho_fonte"] = prev_tamanho
        st.session_state.config_visual["cor_texto"] = prev_cor_texto
        st.session_state.config_visual["cor_fundo_tabela"] = prev_cor_tabela
        salvar_config()
        st.success("✨ Configurações aplicadas e guardadas com sucesso!")
        st.rerun()

  with col_cfg2:
    st.subheader("👁️ Pré-visualização ao Vivo")
    st.markdown(
        "Veja abaixo como o painel e os elementos ficarão com as opções"
        " selecionadas:"
    )
    bg_preview_css = TEMAS_FUNDO.get(
        prev_fundo_app, TEMAS_FUNDO["Gradiente Azul Moderno"]
    )
    preview_html = f"""
        <div style="background: {bg_preview_css}; padding: 25px; border-radius: 14px; border: 2px dashed #007bff; color: {prev_cor_texto}; font-size: {prev_tamanho}; font-family: sans-serif;">
            <h3 style="margin-top:0; color: {prev_cor_texto};">🔍 Exemplo de Cartão RBM</h3>
            <p>Este é o aspeto do texto principal com a fonte <b>{prev_tamanho}</b>.</p>
            <div style="background-color: {prev_cor_tabela}; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-top: 10px;">
                <b>📊 Pré-visualização de Tabela / Bloco:</b><br>
                Produto Exemplo: Calzone Chocolate (12 un)<br>
                Stock: 40 unidades (Setor: Secos e Molhados)
            </div>
            <button style="margin-top: 15px; background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold
