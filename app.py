import datetime
import pandas as pd
import streamlit as st

# Configuração da página orientada ao setor alimentício
st.set_page_config(
    page_title="Gestão de Stock - Alimentício Avançado",
    page_icon="🍲",
    layout="wide",
)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "users" not in st.session_state:
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

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""
  st.session_state.perfil = ""

if "config_visual" not in st.session_state:
  st.session_state.config_visual = {
      "tamanho_fonte": "16px",
      "cor_fundo_tabela": "#f9f9f9",
      "cor_texto": "#31333F",
  }

if "historico" not in st.session_state:
  st.session_state.historico = pd.DataFrame(
      columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"]
  )

if "mensagens" not in st.session_state:
  st.session_state.mensagens = []

if "agenda_eventos" not in st.session_state:
  st.session_state.agenda_eventos = []

if "setores" not in st.session_state:
  st.session_state.setores = [
      "Armazém Central",
      "Câmara Fria",
      "Secos e Molhados",
  ]

if "pedidos_ativos" not in st.session_state:
  st.session_state.pedidos_ativos = {}

if "estoque" not in st.session_state:
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

# Aplicar estilo visual dinâmico & wallpaper moderno
cfg = st.session_state.config_visual
st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-size: {cfg['tamanho_fonte']} !important;
        color: {cfg['cor_texto']} !important;
    }}
    .stApp {{
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }}
    .stDataFrame {{
        background-color: {cfg['cor_fundo_tabela']} !important;
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
  st.title("🍲 RBM Indústria de Alimentos - Controlo de Estoque & Expedição")
  st.markdown("Insira as suas credenciais para aceder ao armazém.")
  user_input = st.text_input("Utilizador")
  pass_input = st.text_input("Senha", type="password")

  if st.button("Entrar no Sistema"):
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
          st.success(f"Utilizador '{novo_user}' guardado!")
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
              st.rerun()

  with tab_adm2:
    with st.container(border=True):
      st.subheader("Gestão de Setores")
      novo_setor = st.text_input("Nome do Novo Setor", key="in_setor")
      if st.button("Adicionar Setor"):
        if novo_setor and novo_setor.strip():
          if novo_setor.strip() not in st.session_state.setores:
            st.session_state.setores.append(novo_setor.strip())
            st.success("Setor criado!")
            st.rerun()
          else:
            st.error("Já existe.")
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
          st.success("Atualizado com sucesso!")
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
        st.success("Produto eliminado!")
        st.rerun()


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
  st.markdown("## ➕ Entradas, Saídas e Registo por Scanner")

  if not permissoes_atuais["pode_movimentar"]:
    st.error("Sem permissão para movimentar stock.")
  else:
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
              st.success(
                  f"Produto adicionado ao setor '{m_setor}' com sucesso!"
              )
              st.rerun()
            else:
              st.error("Preencha o nome e o código de barras.")
    else:
      st.info(
          "ℹ️ Apenas administradores podem cadastrar novos produtos no"
          " catálogo geral."
      )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
      st.subheader("📦 Movimentar Stock (Entrada / Saída)")
      modo_mov = st.radio(
          "Método de Identificação",
          [
              "Selecionar na Lista",
              "Bipar com Câmara Traseira (Scanner)",
              "Digitar Código de Barras",
          ],
          horizontal=True,
      )

      produto_selecionado = None

      if modo_mov == "Selecionar na Lista":
        produto_selecionado = st.selectbox(
            "Produto", df["Produto"].tolist(), key="sel_mov_l"
        )
      elif modo_mov == "Bipar com Câmara Traseira (Scanner)":
        st.info("📸 Aponte a câmara traseira para o código de barras:")
        # Força o uso da câmara traseira com facingMode="environment"
        foto_scanner = st.camera_input(
            "Escanear Código de Barras",
            key="cam_scanner_entrada",
            help="Utiliza a câmara principal/traseira do dispositivo.",
        )
        if foto_scanner is not None:
          bc_foto = st.text_input(
              "Confirme ou digite o código detetado:",
              placeholder="Ex: 789101",
          )
          if bc_foto:
            match = df[df["Codigo_Barras"] == bc_foto]
            if not match.empty:
              produto_selecionado = match.iloc[0]["Produto"]
              st.success(
                  f"✔️ Produto detetado: **{produto_selecionado}** (Setor:"
                  f" {match.iloc[0]['Setor']})"
              )
            else:
              st.error("Código não encontrado no stock.")
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
          st.success(
