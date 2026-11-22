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


def salvar_clientes():
  with open(ARQ_CLIENTES, "w", encoding="utf-8") as f:
    json.dump(st.session_state.clientes, f, ensure_ascii=False)


def salvar_clientes_pedidos():
  with open(ARQ_CLIENTES_PEDIDOS, "w", encoding="utf-8") as f:
    json.dump(st.session_state.clientes_pedidos, f, ensure_ascii=False)


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

if "clientes" not in st.session_state:
  if os.path.exists(ARQ_CLIENTES):
    with open(ARQ_CLIENTES, "r", encoding="utf-8") as f:
      st.session_state.clientes = json.load(f)
  else:
    st.session_state.clientes = [
        {
            "razao_social": "Neriah Comercio de Alimentos LTDA",
            "nome_fantasia": "Neriah Comércio",
            "cnpj": "12.345.678/0001-99",
            "endereco": "Rua Principal, 100 - Florianópolis - SC",
            "contacto": "(48) 99999-9999",
        }
    ]
    salvar_clientes()

if "clientes_pedidos" not in st.session_state:
  if os.path.exists(ARQ_CLIENTES_PEDIDOS):
    with open(ARQ_CLIENTES_PEDIDOS, "r", encoding="utf-8") as f:
      st.session_state.clientes_pedidos = json.load(f)
  else:
    st.session_state.clientes_pedidos = []
    salvar_clientes_pedidos()

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
        "Lote": ["LOT-2026-A", "LOT-2026-B", "LOT-2026-C"],
        "Fabricacao": ["2026-10-01", "2026-09-15", "2026-10-10"],
        "Validade": ["2026-11-15", "2027-05-20", "2026-11-10"],
        "Ultima_Modificacao": ["2026-11-01", "2026-11-05", "2026-11-10"],
        "Modificado_Por": ["admin", "operador", "admin"],
    })
    salvar_estoque()

if "Lote" not in st.session_state.estoque.columns:
  st.session_state.estoque["Lote"] = "LOT-GERAL"

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

# Recarregar mensagens não lidas em tempo real
if os.path.exists(ARQ_MENSAGENS):
  with open(ARQ_MENSAGENS, "r", encoding="utf-8") as f:
    st.session_state.mensagens = json.load(f)

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
    bg_preview_css = TEMAS_FUNDO.get(
        prev_fundo_app, TEMAS_FUNDO["Gradiente Azul Moderno"]
    )
    preview_html = """
        <div style="background: {}; padding: 25px; border-radius: 14px; border: 2px dashed #007bff; color: {}; font-size: {}; font-family: sans-serif;">
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

  hoje_str = datetime.date.today().strftime("%Y-%m-%d")
  total_skus = len(df)
  total_qtd = int(df["Quantidade"].sum()) if not df.empty else 0
  criticos = len(df[df["Quantidade"] <= df["Limite_Minimo"]])
  vencidos = len(df[df["Validade"] <= hoje_str])

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
        df_f["Produto"].str.contains(pesquisa, case=False, na=False)
        | df_f["Codigo_Barras"].str.contains(pesquisa, case=False, na=False)
        | df_f["Lote"].str.contains(pesquisa, case=False, na=False)
    ]


  def estilo_alerta(row):
    val = row.get("Validade", hoje_str)
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

  if not permissoes_atuais["pode_movimentar"]:
    st.error("Sem permissão para movimentar stock.")
  else:
    if st.session_state.perfil == "Administrador":
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
            m_min = st.number_input("Limite Mínimo", min_value=1, value=10)

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
            if m_nome and m_cod:
              nova_l = pd.DataFrame({
                  "Codigo_Barras": [m_cod],
                  "Produto": [m_nome],
                  "Descricao": [m_desc],
                  "Unidades_Embalagem": [m_emb],
                  "Tipo_Item": [m_tipo],
                  "Setor": [m_setor],
                  "Quantidade": [0],
                  "Limite_Minimo": [m_min],
                  "Lote": [m_lote],
                  "Fabricacao": [str(m_fab)],
                  "Validade": [str(m_val)],
                  "Ultima_Modificacao": [
                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                  ],
                  "Modificado_Por": [st.session_state.username],
              })
              st.session_state.estoque = pd.concat(
                  [st.session_state.estoque, nova_l], ignore_index=True
              )
              salvar_estoque()
              st.success(
                  f"Produto e Lote '{m_lote}' registados com sucesso no setor"
                  f" '{m_setor}'!"
              )
              st.rerun()
            else:
              st.error("Preencha o nome e o código de barras.")

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
          match = df[df["Codigo_Barras"] == cod_lido.strip()]
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
        )
        if bc:
          match = df[df["Codigo_Barras"] == bc]
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
          novo_lote_mov = st.text_input("Nº do Lote", value="LOT-2026-X")
        with col_q3:
          data_fab_mov = st.date_input(
              "Fabricação", datetime.date.today(), key="fab_mov_dt"
          )
          data_val_mov = st.date_input(
              "Validade", datetime.date.today(), key="val_mov_dt"
          )

        if st.button("🚀 Confirmar e Registar Movimento", type="primary"):
          idx = df[df["Produto"] == produto_selecionado].index[0]
          setor_reg = df.loc[idx, "Setor"]
          data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

          if "Recebimento" in tipo_op:
            df.loc[idx, "Quantidade"] += qtd_op
            df.loc[idx, "Lote"] = novo_lote_mov
            df.loc[idx, "Fabricacao"] = str(data_fab_mov)
            df.loc[idx, "Validade"] = str(data_val_mov)
            acao = "Recebimento"
          else:
            if df.loc[idx, "Quantidade"] >= qtd_op:
              df.loc[idx, "Quantidade"] -= qtd_op
              acao = "Expedição"
            else:
              st.error("⚠️ Stock insuficiente para realizar esta retirada!")
              st.stop()

          df.loc[idx, "Ultima_Modificacao"] = data_atual
          df.loc[idx, "Modificado_Por"] = st.session_state.username

          nova_hist = pd.DataFrame(
              [[
                  data_atual,
                  st.session_state.username,
                  f"{acao} (Setor {setor_reg} - Lote {novo_lote_mov})",
                  produto_selecionado,
                  qtd_op,
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
        "Número de Cópias de Etiquetas", min_value=1, value=5
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
          " automaticamente todos os 22 itens do talão da Neriah[span_0](start_span)[span_0](end_span)."
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
        if modo_add_ped == "Selecionar do Stock":
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
              {"produto": str(item_sel).strip(), "qtd": qtd_sel}
          )
          st.success(f"Adicionado: {item_sel} ({qtd_sel} un)")
        else:
          st.error("Informe o nome do produto.")

      if st.session_state.temp_itens:
        st.markdown("#### **Itens Adicionados no Pedido Atual:**")
        for it in st.session_state.temp_itens:
          st.write(f"- {it['produto']}: **{it['qtd']} un**")

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
                        "qtd_pedida": i["qtd"],
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
        erro_stk = False
        itens_para_abater = []
        for item in dados_pedido["itens"]:
          p_n = item["produto"]
          q_s = item["qtd_pedida"]
          match_stk = df[df["Produto"] == p_n]
          if not match_stk.empty:
            r_idx = match_stk.index[0]
            if df.loc[r_idx, "Quantidade"] >= q_s:
              itens_para_abater.append(
                  (r_idx, p_n, q_s, df.loc[r_idx, "Setor"])
              )
            else:
              erro_stk = True
              st.error(
                  f"⚠️ Stock insuficiente para **{p_n}** no setor"
                  f" {df.loc[r_idx, 'Setor']} (Disponível:"
                  f" {df.loc[r_idx, 'Quantidade']}, Pedido: {q_s})!"
              )

        if not erro_stk:
          data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
          for r_idx, p_n, q_s, setor_prod in itens_para_abater:
            df.loc[r_idx, "Quantidade"] -= q_s
            df.loc[r_idx, "Ultima_Modificacao"] = data_atual
            df.loc[r_idx, "Modificado_Por"] = st.session_state.username

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
            )
            if scan_codigo:
              match_bar = df[df["Codigo_Barras"] == scan_codigo.strip()]
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
            m_qtd = item["qtd_pedida"]
            a_qtd = item["qtd_separada"]

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
      c_razao = st.text_input("Razão Social")
      c_fantasia = st.text_input("Nome Fantasia")
      c_cnpj = st.text_input("CNPJ", placeholder="00.000.000/0001-00")
      c_end = st.text_area("Endereço Completo")
      c_cont = st.text_input("Contacto (Telefone / E-mail)")

      if st.button("💾 Guardar Novo Cliente", type="primary"):
        if c_razao and c_cnpj:
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
              {"produto": prod_escolhido, "quantidade": qtd_escolhida}
          )
          st.success(f"Adicionado: {prod_escolhido} ({qtd_escolhida} un)")

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
        )

        pedidos_filtrados = [
            p
            for p in st.session_state.clientes_pedidos
            if p["cliente"] == filtro_cli_rel
            and p.get("mes_ano", p["data"][:7]) == filtro_mes
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

          csv_rel = df_rel.to_csv(index=False).encode("utf-8")
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


# --- 6. MENSAGENS (COM SINCRONIZAÇÃO EM TEMPO REAL) ---
elif menu.startswith("💬 Mensagens"):
  st.markdown("## 💬 Central de Mensagens & Bate-Papo Interno")

  # Recarregamento em tempo real do ficheiro para ver mensagens de outros utilizadores
  if os.path.exists(ARQ_MENSAGENS):
    with open(ARQ_MENSAGENS, "r", encoding="utf-8") as f:
      st.session_state.mensagens = json.load(f)

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

    for m in st.session_state.mensagens:
      if (
          m["para"] == st.session_state.username
          and m["de"] == destinatario
          and not m.get("lida", False)
      ):
        m["lida"] = True
    salvar_mensagens()

    st.markdown("---")
    st.markdown(f"### 💬 Conversa com: **{destinatario}**")

    conversa = [
        m
        for m in st.session_state.mensagens
        if (
            (
                m["de"] == st.session_state.username
                and m["para"] == destinatario
            )
            or (m["de"] == destinatario and m["para"] == st.session_state.username)
        )
    ]

    chat_container = st.container(height=350)
    with chat_container:
      if not conversa:
        st.info(f"Sem mensagens ainda com **{destinatario}**.")
      else:
        for msg in conversa:
          remetente = msg["de"]
          texto = msg["texto"]
          data_envio = msg["data"]
          ficheiro_info = msg.get("ficheiro", None)

          if remetente == st.session_state.username:
            st.markdown(
                f"<div style='text-align: right; background-color: #d1e7dd; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%;'>"
                f"<small><b>Você</b> — {data_envio}</small><br>{texto}</div>",
                unsafe_allow_html=True,
            )
            if ficheiro_info:
              st.markdown(
                  f"<div style='text-align: right;'><a"
                  f" href='data:file/txt;base64,{ficheiro_info['dados']}'"
                  f" download='{ficheiro_info['nome']}'>📎 Ficheiro Anexado:"
                  f" {ficheiro_info['nome']}</a></div>",
                  unsafe_allow_html=True,
              )
          else:
            st.markdown(
                f"<div style='text-align: left; background-color: #f8d7da; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;'>"
                f"<small><b>{remetente}</b> — {data_envio}</small><br>{texto}</div>",
                unsafe_allow_html=True,
            )
            if ficheiro_info:
              st.markdown(
                  f"<div style='text-align: left;'><a"
                  f" href='data:file/txt;base64,{ficheiro_info['dados']}'"
                  f" download='{ficheiro_info['nome']}'>📎 Ficheiro Anexado:"
                  f" {ficheiro_info['nome']}</a></div>",
                  unsafe_allow_html=True,
              )

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
          import base64

          d_arquivo = None
          if anexo_arquivo is not None:
            bytes_arq = anexo_arquivo.read()
            b64_arq = base64.b64encode(bytes_arq).decode("utf-8")
            d_arquivo = {"nome": anexo_arquivo.name, "dados": b64_arq}

          # Recarregar antes de adicionar para evitar sobrescrever mensagens de outros
          if os.path.exists(ARQ_MENSAGENS):
            with open(ARQ_MENSAGENS, "r", encoding="utf-8") as f:
              st.session_state.mensagens = json.load(f)

          nova_msg = {
              "de": st.session_state.username,
              "para": destinatario,
              "texto": texto_msg if texto_msg else "[Ficheiro Anexado]",
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


# --- 7. RELATÓRIOS ---
elif menu == "📊 Romaneios & Relatórios":
  st.markdown("## 📊 Relatórios & Romaneios")
  if st.button("Descarregar CSV do Stock"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar Ficheiro", csv, "estoque_rbm.csv", "text/csv"
    )


# --- 8. HISTÓRICO ---
elif menu == "📜 Histórico de Auditoria":
  st.markdown("## 📜 Histórico de Atividades")
  st.dataframe(st.session_state.historico, use_container_width=True)
