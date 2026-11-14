import datetime
import pandas as pd
import streamlit as st

# Configuração da página orientada ao setor alimentício
st.set_page_config(
    page_title="Gestão de Estoque - Alimentício Avançado",
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
      "Validade": ["2026-11-15", "2027-05-20", "2026-11-10"],
      "Ultima_Modificacao": ["2026-11-01", "2026-11-05", "2026-11-10"],
      "Modificado_Por": ["admin", "operador", "admin"],
  })

# Aplicar estilo visual dinâmico
cfg = st.session_state.config_visual
st.markdown(
    f"""
    <style>
    html, body, [class*="css"] {{
        font-size: {cfg['tamanho_fonte']} !important;
        color: {cfg['cor_texto']} !important;
    }}
    .stDataFrame {{
        background-color: {cfg['cor_fundo_tabela']} !important;
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

# --- 1. PAINEL DO ADMINISTRADOR ---
if menu == "⚙️ Painel do Administrador & Agenda":
  st.markdown("## ⚙️ Painel de Controlo do Administrador")
  st.markdown(
      "Gestão centralizada de acessos, setores, calendário, edição rápida,"
      " backup e dados."
  )

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
        if st.button("Guardar Alterações"):
          df.loc[idx_ed, "Produto"] = nn
          df.loc[idx_ed, "Descricao"] = nd
          df.loc[idx_ed, "Unidades_Embalagem"] = ne
          df.loc[idx_ed, "Limite_Minimo"] = nm
          st.success("Atualizado!")
          st.rerun()

  with tab_adm5:
    with st.container(border=True):
      st.subheader("💾 Backup e Restauro de Dados")
      st.markdown(
          "Transfira uma cópia de segurança do seu inventário atual em formato"
          " CSV ou restaure dados anteriores."
      )

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
  st.markdown("## 🍲 Consulta de Stock")
  setor_filtro = st.selectbox(
      "Setor", ["Todos os Setores"] + st.session_state.setores
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
    if row["Quantidade"] <= row["Limite_Minimo"] or row["Validade"] <= hoje:
      return [
          "color: red; font-weight: bold; background-color: #ffe6e6;"
      ] * len(row)
    return [""] * len(row)


  st.dataframe(
      df_f.style.apply(estilo_alerta, axis=1), use_container_width=True
  )


# --- 3. ENTRADAS E SAÍDAS ---
elif menu == "➕ Entradas / Saídas (Expedição)":
  st.markdown("## ➕ Entradas, Saídas e Registo Manual")

  if not permissoes_atuais["pode_movimentar"]:
    st.error("Sem permissão para movimentar stock.")
  else:
    with st.container(border=True):
      cadastrar_novo_manual = st.checkbox(
          "➕ Adicionar Novo Produto Manualmente ao Catálogo"
      )
      if cadastrar_novo_manual:
        st.subheader("Registo Manual de Novo Item")
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
              "Tipo", ["Produto Acabado", "Matéria-Prima", "Insumo", "Embalagem"]
          )
          m_setor = st.selectbox("Setor", st.session_state.setores)
          m_min = st.number_input("Limite Mínimo", min_value=1, value=10)

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
                "Validade": [datetime.date.today().strftime("%Y-%m-%d")],
                "Ultima_Modificacao": [
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                ],
                "Modificado_Por": [st.session_state.username],
            })
            st.session_state.estoque = pd.concat(
                [st.session_state.estoque, nova_l], ignore_index=True
            )
            st.success("Produto adicionado manualmente ao stock!")
            st.rerun()
          else:
            st.error("Preencha o nome e o código de barras.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
      st.subheader("📦 Movimentar Stock (Entrada / Saída)")
      modo_mov = st.radio(
          "Método",
          ["Selecionar na Lista", "Bipar Código de Barras"],
          horizontal=True,
      )
      prod_mov = None
      if modo_mov == "Selecionar na Lista":
        prod_mov = st.selectbox(
            "Produto", df["Produto"].tolist(), key="sel_mov_l"
        )
      else:
        bc = st.text_input("Bipar Código de Barras", key="bc_mov")
        if bc:
          m = df[df["Codigo_Barras"] == bc]
          if not m.empty:
            prod_mov = m.iloc[0]["Produto"]
            st.success(f"Encontrado: {prod_mov}")
          else:
            st.error("Não encontrado.")

      if prod_mov:
        tipo_op = st.radio(
            "Operação",
            ["Recebimento (Entrada)", "Baixa (Saída)"],
            horizontal=True,
        )
        qtd_op = st.number_input(
            "Quantidade", min_value=1, value=1, key="qtd_mov_val"
        )
        if st.button("Registar Movimento"):
          idx = df[df["Produto"] == prod_mov].index[0]
          if "Recebimento" in tipo_op:
            df.loc[idx, "Quantidade"] += qtd_op
          else:
            if df.loc[idx, "Quantidade"] >= qtd_op:
              df.loc[idx, "Quantidade"] -= qtd_op
            else:
              st.error("Stock insuficiente!")
              st.stop()
          st.success("Movimento registado com sucesso!")


# --- 4. GESTÃO DE PEDIDOS & CHECK-LIST (Com Câmara Traseira Forçada) ---
elif menu == "📋 Gestão de Pedidos & Check-list":
  st.markdown("## 📋 Setor de Separação de Pedidos & Check-list")
  st.markdown(
      "Tire foto do talão ou adicione itens manualmente para gerar a lista de"
      " separação."
  )

  with st.container(border=True):
    st.subheader("📸 1. Criar Pedido (Via Câmara Traseira ou Manual)")
    tipo_cap = st.radio(
        "Origem do Pedido",
        [
            "Tirar Foto com a Câmara Traseira",
            "Carregar Ficheiro",
            "Apenas Inserção Manual",
        ],
        horizontal=True,
    )
    img_ped = None
    if tipo_cap == "Tirar Foto com a Câmara Traseira":
      # Força o uso da câmara traseira através do parâmetro facingMode
      img_ped = st.camera_input(
          "Aponte para o talão do pedido",
          key="cam_traseira_talao",
          help="Certifique-se de permitir o acesso à câmara no browser.",
      )
    elif tipo_cap == "Carregar Ficheiro":
      img_ped = st.file_uploader("Ficheiro do talão", type=["png", "jpg"])

    cli_nome = st.text_input(
        "Nome do Cliente / Destino", placeholder="Ex: Neriah Comércio"
    )

    if img_ped:
      st.image(img_ped, width=300)
      st.success("Talão capturado com sucesso!")

    st.markdown("---")
    st.subheader("Adicionar Itens ao Pedido (Seleção ou Digitação Manual)")

    if "temp_itens" not in st.session_state:
      st.session_state.temp_itens = []

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
            "Nome do Produto Manual / Personalizado", key="txt_item_ped_manual"
        )
    with c_p2:
      qtd_sel = st.number_input(
          "Quantidade", min_value=1, value=1, key="qtd_item_ped"
      )

    if st.button("Adicionar Item à Lista do Pedido"):
      if item_sel and str(item_sel).strip():
        st.session_state.temp_itens.append(
            {"produto": str(item_sel).strip(), "qtd": qtd_sel}
        )
        st.success(f"Adicionado: {item_sel} ({qtd_sel} un)")
      else:
        st.error("Informe o nome do produto.")

    if st.session_state.temp_itens:
      st.write("**Itens no Pedido Atual:**")
      for it in st.session_state.temp_itens:
        st.write(f"- {it['produto']}: **{it['qtd']} un**")

      if st.button("🚀 Gerar Setor de Separação para este Pedido"):
        if cli_nome:
          pid = f"Pedido_{datetime.datetime.now().strftime('%H%M%S')}"
          st.session_state.pedidos_ativos[pid] = {
              "cliente": cli_nome,
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
          st.success(f"Setor de separação criado com ID: {pid}!")
          st.rerun()
        else:
          st.error("Insira o nome do cliente.")

  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown("### 📦 2. Setores de Separação Ativos (Leitor de Barras)")

  if not st.session_state.pedidos_ativos:
    st.info("Nenhum pedido em separação no momento.")
  else:
    for pid, pdata in st.session_state.pedidos_ativos.items():
      stato = "✅ Separado" if pdata["concluido"] else "⏳ Em Separação"
      with st.expander(
          f"📦 {pid} — Cliente: **{pdata['cliente']}** [{stato}]",
          expanded=not pdata["concluido"],
      ):
        scan_codigo = st.text_input(
            f"🔍 Escanear Código de Barras do Produto ({pid})",
            key=f"scan_sep_{pid}",
            placeholder="Passe o leitor de barras para separar 1 unidade...",
        )
        if scan_codigo:
          match_bar = df[df["Codigo_Barras"] == scan_codigo]
          if not match_bar.empty:
            nome_prod_encontrado = match_bar.iloc[0]["Produto"]
            achou_no_pedido = False
            for itm in pdata["itens"]:
              if itm["produto"] == nome_prod_encontrado:
                achou_no_pedido = True
                if itm["qtd_separada"] < itm["qtd_pedida"]:
                  itm["qtd_separada"] += 1
                  st.success(
                      f"✔️ Separado 1 unidade de {nome_prod_encontrado}! Progresso:"
                      f" {itm['qtd_separada']}/{itm['qtd_pedida']}"
                  )
                  st.rerun()
                else:
                  st.warning(
                      f"O item {nome_prod_encontrado} já está completo neste"
                      " pedido!"
                  )
            if not achou_no_pedido:
              st.error(
                  f"O produto '{nome_prod_encontrado}' não pertence a este"
                  " pedido!"
              )
          else:
            st.error("Código de barras desconhecido!")

        st.markdown("---")
        todos_ok = True
        for i_idx, item in enumerate(pdata["itens"]):
          p_name = item["produto"]
          m_qtd = item["qtd_pedida"]
          a_qtd = item["qtd_separada"]

          estilo_cor = (
              "color: #28a745; font-weight: bold; background-color: #e8f5e9;"
              " padding: 4px 8px; border-radius: 4px;"
              if a_qtd >= m_qtd
              else "color: #333;"
          )

          col1, col2, col3 = st.columns([3, 2, 2])
          with col1:
            st.markdown(
                f"<span style='{estilo_cor}'>{p_name}</span>",
                unsafe_allow_html=True,
            )
          with col2:
            st.markdown(
                f"<span style='{estilo_cor}'>Separado: **{a_qtd}/{m_qtd}**</span>",
                unsafe_allow_html=True,
            )
          with col3:
            b_mais = st.button("➕", key=f"mais_{pid}_{i_idx}")
            b_menos = st.button("➖", key=f"menos_{pid}_{i_idx}")
            if b_mais and a_qtd < m_qtd:
              item["qtd_separada"] += 1
              st.rerun()
            if b_menos and a_qtd > 0:
              item["qtd_separada"] -= 1
              st.rerun()

          if a_qtd < m_qtd:
            todos_ok = False

        st.markdown("<br>", unsafe_allow_html=True)
        if not todos_ok:
          st.warning(
              "⚠️ Separação em andamento. Escaneie os códigos de barras ou use"
              " os botões para concluir."
          )
        else:
          st.success(
              "✨ **Todos os itens deste pedido foram separados com sucesso"
              " (Verde)!**"
          )
          if not pdata["concluido"]:
            if st.button(
                f"📥 Confirmar e Dar Baixa Definitiva no Stock ({pid})",
                key=f"baixar_{pid}",
            ):
              erro_stk = False
              for item in pdata["itens"]:
                p_n = item["produto"]
                q_s = item["qtd_pedida"]
                match_stk = df[df["Produto"] == p_n]
                if not match_stk.empty:
                  r_idx = match_stk.index[0]
                  if df.loc[r_idx, "Quantidade"] >= q_s:
                    df.loc[r_idx, "Quantidade"] -= q_s
                  else:
                    erro_stk = True
                    st.error(f"Stock insuficiente para {p_n}!")

              if not erro_stk:
                pdata["concluido"] = True
                st.success(
                    "Baixa de stock efetuada com sucesso para todo o pedido!"
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
