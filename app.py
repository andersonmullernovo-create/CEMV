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

# Dicionário de temas de fundo / papéis de parede disponíveis
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
  st.session_state.mensagens = []

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

# Obter estilos visuais atuais
cfg = st.session_state.config_visual
bg_css = TEMAS_FUNDO.get(
    cfg.get("fundo_app", "Gradiente Azul Moderno"), TEMAS_FUNDO["Gradiente Azul Moderno"]
)

# Estilo visual global & bloqueio de menu de toque longo do Android
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

# --- SISTEMA DE LOGIN (ESTILIZADO COM TEMA CONFIGURÁVEL) ---
if not st.session_state.logged_in:
  bg_login_css = TEMAS_FUNDO.get(
      cfg.get("fundo_login", "Gradiente Azul Moderno"),
      TEMAS_FUNDO["Gradiente Azul Moderno"],
  )

  # Aplicar fundo específico da tela de login se necessário
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
    if m["para"] == st.session_state.username and not m["lida"]
]
num_novas = len(msgs_nao_lidas)

if num_novas > 0:
  st.sidebar.warning(f"🔔 Tem {num_novas} nova(s) mensagem(ns)!")

opcoes_menu = [
    "🍲 Consultar Stock & Setores",
    "➕ Entradas / Saídas (Expedição)",
    "📋 Gestão de Pedidos & Check-list",
    f"💬 Mensagens & Ficheiros ({num_novas})",
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

# --- 1. PAINEL DO ADMINISTRADOR (Exclusivo para Administradores) ---
if menu == "⚙️ Painel do Administrador & Agenda":
  if st.session_state.perfil != "Administrador":
    st.error(
        "⚠️ Acesso restrito! Apenas administradores podem aceder a este"
        " painel."
    )
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


# --- PÁGINA DE CONFIGURAÇÃO VISUAL & PRÉ-VISUALIZAÇÃO ---
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

      # Inputs de configuração (interativos para preview em tempo real)
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

    # Caixa simulando a pré-visualização em tempo real
    preview_html = f"""
        <div style="background: {bg_preview_css}; padding: 25px; border-radius: 14px; border: 2px dashed #007bff; color: {prev_cor_texto}; font-size: {prev_tamanho}; font-family: sans-serif;">
            <h3 style="margin-top:0; color: {prev_cor_texto};">🔍 Exemplo de Cartão RBM</h3>
            <p>Este é o aspeto do texto principal com a fonte <b>{prev_tamanho}</b>.</p>
            <div style="background-color: {prev_cor_tabela}; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-top: 10px;">
                <b>📊 Pré-visualização de Tabela / Bloco:</b><br>
                Produto Exemplo: Calzone Chocolate (12 un)<br>
                Stock: 40 unidades (Setor: Secos e Molhados)
            </div>
            <button style="margin-top: 15px; background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer;">Botão de Exemplo</button>
        </div>
        """
    st.markdown(preview_html, unsafe_allow_html=True)
    st.caption(
        "💡 Nota: O tema de login selecionado será aplicado assim que terminar"
        " sessão."
    )


# --- 2. CONSULTAR STOCK ---
elif menu == "🍲 Consultar Stock & Setores":
  st.markdown("## 🍲 Consulta de Stock por Setor")
  setor_filtro = st.selectbox(
      "Filtrar por Setor", ["Todos os Setores"] + st.session_state.setores
  )
  pesquisa = st.text_input("🔍 Pesquisar por Produto ou Código", "")

  df_f = df.copy()
  if setor_filtro != "Todos os Setores":
    df_f = df_f[df_f["Setor"] == setor_filtro]
  if pesquisa:
    df_f = df_f[
        df_f["Produto"].str.contains(pesquisa, case=False, na=False)
        | df_f["Codigo_Barras"].str.contains(pesquisa, case=False, na=False)
    ]


  def estilo_alerta(row):
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    val = row.get("Validade", hoje)
    if row["Quantidade"] <= row["Limite_Minimo"] or val <= hoje:
      return [
          "color: red; font-weight: bold; background-color: #ffe6e6;"
      ] * len(row)
    return [""] * len(row)


  st.dataframe(
      df_f.style.apply(estilo_alerta, axis=1), use_container_width=True
  )


# --- 3. ENTRADAS E SAÍDAS ---
elif menu == "➕ Entradas / Saídas (Expedição)":
  st.markdown("## ➕ Entradas, Saídas e Leitura por Câmara (Tempo Real)")

  if not permissoes_atuais["pode_movimentar"]:
    st.error("Sem permissão para movimentar stock.")
  else:
    # BLOCO EXCLUSIVO DO ADMINISTRADOR PARA CADASTRAR NOVO PRODUTO
    if st.session_state.perfil == "Administrador":
      with st.container(border=True):
        cadastrar_novo_manual = st.checkbox(
            "➕ [Admin] Adicionar Novo Produto Manualmente ao Catálogo"
        )
        if cadastrar_novo_manual:
          st.subheader("Registo Manual de Novo Item no Catálogo")
          col_m1, col_m2 = st.columns(2)
          with col_m1:
            m_nome = st.text_input("Nome do Produto")
            m_cod = st.text_input("Código de Barras")
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
                "Data de Fabricação (Novo Item)", datetime.date.today()
            )
          with col_d2:
            m_val = st.date_input(
                "Data de Validade (Novo Item)", datetime.date.today()
            )

          if st.button("Guardar Novo Produto Manual"):
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
                  f"Produto adicionado ao setor '{m_setor}' e guardado com"
                  " sucesso!"
              )
              st.rerun()
            else:
              st.error("Preencha o nome e o código de barras.")
    else:
      st.info(
          "ℹ️ *Nota:* O registo de novos produtos no catálogo geral é restrito"
          " ao perfil de Administrador."
      )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
      st.subheader("📦 Movimentar Stock (Entrada / Saída)")
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
                f"🎯 Produto Encontrado: **{produto_selecionado}** (Setor:"
                f" {match.iloc[0]['Setor']})"
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
                f"Encontrado: **{produto_selecionado}** (Setor:"
                f" {match.iloc[0]['Setor']})"
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

        col_q1, col_q2 = st.columns(2)
        with col_q1:
          qtd_op = st.number_input(
              "Quantidade a Movimentar", min_value=1, value=1, key="qtd_mov_val"
          )
        with col_q2:
          data_fab_mov = st.date_input(
              "Data de Fabricação do Lote",
              datetime.date.today(),
              key="fab_mov_dt",
          )
          data_val_mov = st.date_input(
              "Data de Validade do Lote",
              datetime.date.today(),
              key="val_mov_dt",
          )

        if st.button("🚀 Confirmar e Registar Movimento", type="primary"):
          idx = df[df["Produto"] == produto_selecionado].index[0]
          setor_reg = df.loc[idx, "Setor"]
          data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

          if "Recebimento" in tipo_op:
            df.loc[idx, "Quantidade"] += qtd_op
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
                  f"{acao} (Setor {setor_reg})",
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
              f"Operação de {acao} registada com sucesso no setor **{setor_reg}**!"
          )
          if "codigo_lido_ativo" in st.session_state:
            del st.session_state["codigo_lido_ativo"]


# --- 4. GESTÃO DE PEDIDOS & CHECK-LIST ---
elif menu == "📋 Gestão de Pedidos & Check-list":
  st.markdown("## 📋 Setor de Separação de Pedidos & Check-list")
  st.markdown(
      "Importe o talão, gere o pedido e separe os itens com leitor ótico ou"
      " câmara."
  )

  sub_tab1, sub_tab2 = st.tabs([
      "📸 Criar Novo Pedido (Importação / Manual)",
      "📦 Ver Pedidos Salvos & Ativos",
  ])

  with sub_tab1:
    with st.container(border=True):
      st.subheader("1. Capturar ou Inserir Dados do Pedido")
      tipo_cap = st.radio(
          "Origem do Pedido",
          [
              "Carregar Ficheiro de Talão",
              "Apenas Inserção Manual",
          ],
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
          f" automaticamente todos os 22 itens do talão da Neriah[span_0](start_span)[span_0](end_span)."
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
      st.info(
          "ℹ️ Nenhum pedido registado ou em separação no momento. Crie um na"
          " aba ao lado."
      )
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
            st.success(
                "✅ **Pedido Finalizado:** Os itens foram removidos com sucesso"
                " dos respetivos setores e registados no histórico."
            )
          elif not todos_ok:
            st.warning(
                "⚠️ Separação em andamento. Leia os códigos de barras no setor"
                " correspondente ou use os botões."
            )
          else:
            if "Automática" in modo_baixa:
              sucesso = executar_baixa_pedido(pid, pdata)
              if sucesso:
                st.success(
                    "⚡ **Baixa Automática por Setor Concluída!** Os itens foram"
                    " retirados dos seus setores de origem."
                )
                st.rerun()
            else:
              st.success(
                  "✨ **Todos os itens separados (Verde)!** Pronto para"
                  " conferência."
              )
              if st.button(
                  f"📥 Confirmar e Dar Baixa Manual nos Setores ({pid})",
                  key=f"baixar_{pid}",
                  type="primary",
              ):
                sucesso = executar_baixa_pedido(pid, pdata)
                if sucesso:
                  st.success(
                      "✅ Baixa manual efetuada com sucesso nos setores de"
                      " origem!"
                  )
                  st.rerun()


# --- 5. MENSAGENS ---
elif menu.startswith("💬 Mensagens"):
  st.markdown("## 💬 Central de Mensagens")
  dest = st.selectbox(
      "Para",
      [
          u
          for u in st.session_state.users.keys()
          if u != st.session_state.username
      ],
  )
  txt = st.text_area("Mensagem")
  if st.button("Enviar"):
    st.session_state.mensagens.append({
        "de": st.session_state.username,
        "para": dest,
        "texto": txt,
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "lida": False,
    })
    st.success("Enviado!")


# --- 6. RELATÓRIOS ---
elif menu == "📊 Romaneios & Relatórios":
  st.markdown("## 📊 Relatórios & Romaneios")
  if st.button("Descarregar CSV do Stock"):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar Ficheiro", csv, "estoque_rbm.csv", "text/csv"
    )


# --- 7. HISTÓRICO ---
elif menu == "📜 Histórico de Auditoria":
  st.markdown("## 📜 Histórico de Atividades")
  st.dataframe(st.session_state.historico, use_container_width=True)
