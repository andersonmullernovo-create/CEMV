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

# --- 1. PAINEL DO ADMINISTRADOR (Visual Moderno) ---
if menu == "⚙️ Painel do Administrador & Agenda":
  st.markdown("## ⚙️ Painel de Controlo do Administrador")
  st.markdown(
      "Gestão centralizada de acessos, setores, calendário, edição rápida de"
      " dados e personalização."
  )

  tab_adm1, tab_adm2, tab_adm3, tab_adm4, tab_adm5 = st.tabs([
      "👥 Utilizadores & Permissões",
      "🏢 Setores",
      "📅 Calendário & Agenda",
      "✏️ Edição de Itens",
      "🎨 Visual & Eliminação",
  ])

  with tab_adm1:
    with st.container(border=True):
      st.subheader("Registar ou Modificar Utilizador")
      novo_user = st.text_input(
          "Nome do Utilizador", placeholder="Ex: joao.silva"
      )
      nova_senha = st.text_input("Senha de Acesso", type="password")
      novo_perfil = st.selectbox(
          "Perfil de Acesso", ["Operador", "Administrador"]
      )

      col_perm1, col_perm2, col_perm3 = st.columns(3)
      with col_perm1:
        pode_cad = st.checkbox("Pode Cadastrar Itens", value=True)
      with col_perm2:
        pode_exc = st.checkbox("Pode Excluir Itens", value=False)
      with col_perm3:
        pode_mov = st.checkbox("Pode Movimentar Stock", value=True)

      if st.button("💾 Guardar / Registar Utilizador"):
        if novo_user and nova_senha:
          st.session_state.users[novo_user] = {
              "senha": nova_senha,
              "perfil": novo_perfil,
              "pode_cadastrar": pode_cad,
              "pode_excluir": pode_exc,
              "pode_movimentar": pode_mov,
          }
          st.success(f"Utilizador '{novo_user}' guardado com sucesso!")
        else:
          st.error("Preencha o nome e a senha.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Utilizadores Atuais & Controlo")
    for u, dados in list(st.session_state.users.items()):
      with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
          st.write(f"👤 **{u}** — Perfil: *{dados['perfil']}*")
        with c2:
          if u != "admin":
            if st.button(f"🗑️ Excluir #{u}", key=f"del_user_{u}"):
              del st.session_state.users[u]
              st.success(f"Utilizador {u} eliminado!")
              st.rerun()

  with tab_adm2:
    with st.container(border=True):
      st.subheader("Gestão de Setores de Armazenamento")
      novo_setor = st.text_input(
          "Nome do Novo Setor",
          key="input_novo_setor_adm",
          placeholder="Ex: Câmara de Congelados",
      )

      if st.button("➕ Adicionar Setor"):
        if novo_setor and novo_setor.strip():
          if novo_setor.strip() not in st.session_state.setores:
            st.session_state.setores.append(novo_setor.strip())
            st.success(f"Setor '{novo_setor.strip()}' criado com sucesso!")
            st.rerun()
          else:
            st.error("Este setor já existe!")
        else:
          st.error("Insira um nome válido.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Setores Atuais")
    for s in list(st.session_state.setores):
      with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
          st.write(f"🏭 **{s}**")
        with c2:
          if len(st.session_state.setores) > 1:
            if st.button(f"Excluir", key=f"del_setor_{s}"):
              st.session_state.setores.remove(s)
              st.success(f"Setor {s} removido!")
              st.rerun()
          else:
            st.caption("Mínimo 1 setor")

  with tab_adm3:
    with st.container(border=True):
      st.subheader("📅 Calendário & Agenda de Eventos")
      data_evento = st.date_input("Data do Evento")
      desc_evento = st.text_input(
          "Descrição do Evento", placeholder="Ex: Inventário geral do armazém"
      )

      if st.button("📌 Adicionar Evento à Agenda"):
        if desc_evento:
          st.session_state.agenda_eventos.append(
              {"data": str(data_evento), "evento": desc_evento}
          )
          st.success("Evento adicionado com sucesso!")
        else:
          st.error("Escreva a descrição do evento.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Eventos Agendados")
    if not st.session_state.agenda_eventos:
      st.info("Nenhum evento agendado.")
    else:
      for ev in st.session_state.agenda_eventos:
        st.markdown(f"- 📅 **{ev['data']}**: {ev['evento']}")

  with tab_adm4:
    with st.container(border=True):
      st.subheader("✏️ Edição Rápida de Dados Cadastrados")
      prod_editar = st.selectbox(
          "Selecione o produto para editar detalhes",
          df["Produto"].tolist(),
          key="sel_edit_prod",
      )

      if prod_editar:
        idx_ed = df[df["Produto"] == prod_editar].index[0]
        col_e1, col_e2 = st.columns(2)
        with col_e1:
          novo_nome_ed = st.text_input(
              "Nome do Produto",
              value=df.loc[idx_ed, "Produto"],
              key="ed_nome",
          )
          novo_desc_ed = st.text_area(
              "Descrição", value=df.loc[idx_ed, "Descricao"], key="ed_desc"
          )
          novo_emb_ed = st.number_input(
              "Unidades por Embalagem",
              min_value=1,
              value=int(df.loc[idx_ed, "Unidades_Embalagem"]),
              key="ed_emb",
          )
        with col_e2:
          tipos_disp = ["Matéria-Prima", "Produto Acabado", "Insumo", "Embalagem"]
          tipo_atual = df.loc[idx_ed, "Tipo_Item"]
          idx_tipo = (
              tipos_disp.index(tipo_atual) if tipo_atual in tipos_disp else 0
          )
          novo_tipo_ed = st.selectbox(
              "Tipo de Item", tipos_disp, index=idx_tipo, key="ed_tipo"
          )

          setor_atual = df.loc[idx_ed, "Setor"]
          idx_setor = (
              st.session_state.setores.index(setor_atual)
              if setor_atual in st.session_state.setores
              else 0
          )
          novo_setor_ed = st.selectbox(
              "Setor", st.session_state.setores, index=idx_setor, key="ed_setor"
          )

          novo_min_ed = st.number_input(
              "Limite Mínimo",
              min_value=0,
              value=int(df.loc[idx_ed, "Limite_Minimo"]),
              key="ed_min",
          )

        if st.button("💾 Guardar Alterações do Item"):
          df.loc[idx_ed, "Produto"] = novo_nome_ed
          df.loc[idx_ed, "Descricao"] = novo_desc_ed
          df.loc[idx_ed, "Unidades_Embalagem"] = novo_emb_ed
          df.loc[idx_ed, "Tipo_Item"] = novo_tipo_ed
          df.loc[idx_ed, "Setor"] = novo_setor_ed
          df.loc[idx_ed, "Limite_Minimo"] = novo_min_ed
          df.loc[idx_ed, "Ultima_Modificacao"] = datetime.datetime.now().strftime(
              "%Y-%m-%d %H:%M"
          )
          df.loc[idx_ed, "Modificado_Por"] = st.session_state.username
          st.success(f"Item '{novo_nome_ed}' atualizado com sucesso!")
          st.rerun()

  with tab_adm5:
    with st.container(border=True):
      st.subheader("🎨 Personalização Visual")
      tamanho_escolhido = st.selectbox(
          "Tamanho da Fonte", ["14px", "16px", "18px"], index=1
      )
      cor_texto_escolhida = st.color_picker(
          "Cor Principal do Texto", cfg["cor_texto"]
      )
      cor_tabela_escolhida = st.color_picker(
          "Cor Fundo Tabelas", cfg["cor_fundo_tabela"]
      )

      if st.button("Aplicar Estilo Visual"):
        st.session_state.config_visual["tamanho_fonte"] = tamanho_escolhido
        st.session_state.config_visual["cor_texto"] = cor_texto_escolhida
        st.session_state.config_visual["cor_fundo_tabela"] = (
            cor_tabela_escolhida
        )
        st.success("Estilo atualizado com sucesso!")
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
      st.subheader("🗑️ Eliminar Item do Stock")
      produto_a_excluir = st.selectbox(
          "Selecione o produto a remover permanentemente",
          df["Produto"].tolist(),
          key="excluir_prod",
      )

      if st.button("❌ Confirmar Eliminação do Produto", type="primary"):
        idx_excluir = df[df["Produto"] == produto_a_excluir].index[0]
        st.session_state.estoque = df.drop(idx_excluir).reset_index(drop=True)
        st.success("Produto eliminado com sucesso!")
        st.rerun()


# --- 2. CONSULTAR STOCK & SETORES (Visual Moderno & Cartões) ---
elif menu == "🍲 Consultar Stock & Setores":
  st.markdown("## 🍲 Gestão e Consulta de Stock")
  st.markdown(
      "Consulte em tempo real os níveis de stock, validades e distribuição por"
      " setor."
  )

  total_produtos = len(df)
  total_itens_stock = df["Quantidade"].sum()
  produtos_criticos = len(df[df["Quantidade"] <= df["Limite_Minimo"]])

  col_m1, col_m2, col_m3 = st.columns(3)

  with col_m1:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 18px; border-radius: 10px; border-left: 5px solid #ff4b4b; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #555; font-size: 14px; font-weight: 600;">TOTAL DE PRODUTOS</p>
            <h3 style="margin: 5px 0 0 0; color: #111; font-size: 24px;">{total_produtos}</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )

  with col_m2:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 18px; border-radius: 10px; border-left: 5px solid #ffa500; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #555; font-size: 14px; font-weight: 600;">UNIDADES EM STOCK</p>
            <h3 style="margin: 5px 0 0 0; color: #111; font-size: 24px;">{total_itens_stock} un</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )

  with col_m3:
    st.markdown(
        f"""
        <div style="background-color: #f8f9fa; padding: 18px; border-radius: 10px; border-left: 5px solid #dc3545; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <p style="margin: 0; color: #555; font-size: 14px; font-weight: 600;">ITENS EM ALERTA (MÍNIMO)</p>
            <h3 style="margin: 5px 0 0 0; color: #dc3545; font-size: 24px;">{produtos_criticos}</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)

  with st.container(border=True):
    st.subheader("🔍 Painel de Filtros e Pesquisa")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      setor_filtro = st.selectbox(
          "Filtrar por Setor", ["Todos os Setores"] + st.session_state.setores
      )
    with col_f2:
      pesquisa = st.text_input(
          "Pesquisar por Alimento ou Código de Barras",
          placeholder="Digite para filtrar...",
      )

  df_filtrado = df.copy()
  if setor_filtro != "Todos os Setores":
    df_filtrado = df_filtrado[df_filtrado["Setor"] == setor_filtro]

  if pesquisa:
    df_filtrado = df_filtrado[
        df_filtrado["Produto"].str.contains(pesquisa, case=False, na=False)
        | df_filtrado["Codigo_Barras"].str.contains(
            pesquisa, case=False, na=False
        )
    ]


  def destacar_estoque_e_validade(row):
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    if row["Quantidade"] <= row["Limite_Minimo"] or row["Validade"] <= hoje:
      return [
          "color: red; font-weight: bold; background-color: #ffe6e6;"
      ] * len(row)
    return [""] * len(row)


  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown("### 📋 Tabela de Inventário Atualizada")
  st.dataframe(
      df_filtrado.style.apply(destacar_estoque_e_validade, axis=1),
      use_container_width=True,
  )
  st.caption(
      "🔴 Itens destacados a vermelho indicam stock abaixo do limite mínimo ou"
      " validade vencida/próxima."
  )


# --- 3. ENTRADAS E SAÍDAS (Visual Moderno) ---
elif menu == "➕ Entradas / Saídas (Expedição)":
  st.markdown("## ➕ Registo de Recebimento ou Expedição")
  st.markdown(
      "Faça o controlo de entradas de mercadorias ou retiradas de stock para"
      " expedição."
  )

  if not permissoes_atuais["pode_movimentar"]:
    st.error("⚠️ O seu perfil não tem permissão para movimentar stock.")
  else:
    if permissoes_atuais["pode_cadastrar"]:
      with st.container(border=True):
        cadastrar_novo = st.checkbox(
            "➕ O produto não existe? Cadastrar novo item manualmente"
        )
        if cadastrar_novo:
          st.subheader("Registar Novo Item no Catálogo")
          col_cn1, col_cn2 = st.columns(2)
          with col_cn1:
            novo_prod_nome = st.text_input(
                "Nome do Alimento", placeholder="Ex: Calzone Frango Catupiry"
            )
            novo_prod_cod = st.text_input(
                "Código de Barras", placeholder="Ex: 789..."
            )
            novo_prod_desc = st.text_area("Descrição detalhada")
          with col_cn2:
            novo_un_emb = st.number_input(
                "Unidades por Embalagem", min_value=1, value=1
            )
            novo_tipo = st.selectbox(
                "Tipo de Item",
                ["Matéria-Prima", "Produto Acabado", "Insumo", "Embalagem"],
            )
            novo_prod_setor = st.selectbox(
                "Setor de Armazenamento", st.session_state.setores
            )
            novo_limite = st.number_input(
                "Limite Mínimo de Alerta", min_value=1, value=10
            )

          if st.button("💾 Guardar Novo Item no Stock"):
            if novo_prod_nome and novo_prod_cod:
              nova_linha = pd.DataFrame({
                  "Codigo_Barras": [novo_prod_cod],
                  "Produto": [novo_prod_nome],
                  "Descricao": [novo_prod_desc],
                  "Unidades_Embalagem": [novo_un_emb],
                  "Tipo_Item": [novo_tipo],
                  "Setor": [novo_prod_setor],
                  "Quantidade": [0],
                  "Limite_Minimo": [novo_limite],
                  "Validade": [datetime.date.today().strftime("%Y-%m-%d")],
                  "Ultima_Modificacao": [
                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                  ],
                  "Modificado_Por": [st.session_state.username],
              })
              st.session_state.estoque = pd.concat(
                  [st.session_state.estoque, nova_linha], ignore_index=True
              )
              st.success("Produto cadastrado com sucesso!")
              st.rerun()
            else:
              st.error("Preencha o nome e o código de barras do produto.")

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
      st.subheader("📦 Registar Movimentação de Stock")

      modo_entrada = st.radio(
          "Método de Identificação",
          ["Selecionar na Lista", "Digitar / Bipar Código de Barras"],
          horizontal=True,
      )

      produto_selecionado = None
      if modo_entrada == "Selecionar na Lista":
        produto_selecionado = st.selectbox(
            "Selecione o Produto", df["Produto"].tolist()
        )
      else:
        cod_leitor = st.text_input(
            "Aponte o leitor ou digite o Código de Barras",
            placeholder="Passe o leitor aqui...",
        )
        if cod_leitor:
          match = df[df["Codigo_Barras"] == cod_leitor]
          if not match.empty:
            produto_selecionado = match.iloc[0]["Produto"]
            st.success(f"Item detetado: **{produto_selecionado}**")
          else:
            st.error("Código de barras não registado no sistema!")

      if produto_selecionado:
        st.markdown("---")
        tipo_mov = st.radio(
            "Tipo de Operação",
            ["Recebimento (Entrada)", "Expedição / Baixa (Retirada)"],
            horizontal=True,
        )

        col_m1, col_m2 = st.columns(2)
        with col_m1:
          qtd_mov = st.number_input(
              "Quantidade a Movimentar", min_value=1, step=1, value=1
          )
        with col_m2:
          nova_validade = (
              st.date_input("Data de Validade do Lote", datetime.date.today())
              if "Recebimento" in tipo_mov
              else None
          )

        anexo = st.file_uploader(
            "Anexar Nota Fiscal / Certificado (Opcional)",
            type=["pdf", "png", "jpg"],
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(
            "🚀 Confirmar e Registar Operação", use_container_width=True
        ):
          idx = df[df["Produto"] == produto_selecionado].index[0]
          data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

          if "Recebimento" in tipo_mov:
            df.loc[idx, "Quantidade"] += qtd_mov
            if nova_validade:
              df.loc[idx, "Validade"] = str(nova_validade)
            acao = "Recebimento"
          else:
            if df.loc[idx, "Quantidade"] >= qtd_mov:
              df.loc[idx, "Quantidade"] -= qtd_mov
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
                  acao,
                  produto_selecionado,
                  qtd_mov,
              ]],
              columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
          )
          st.session_state.historico = pd.concat(
              [st.session_state.historico, nova_hist], ignore_index=True
          )
          st.success(f"Operação de {acao} registada com sucesso no sistema!")


# --- 4. GESTÃO DE PEDIDOS & CHECK-LIST (Visual Moderno & Câmara) ---
elif menu == "📋 Gestão de Pedidos & Check-list":
  st.markdown("## 📋 Gestão de Pedidos e Check-list")
  st.markdown(
      "Escanear talões, gerir listas de separação e dar baixa automática no"
      " stock."
  )

  with st.container(border=True):
    st.subheader("📸 1. Registo e Escaneamento de Pedido")

    tipo_captura = st.radio(
        "Origem da Imagem do Pedido",
        ["Tirar Foto com a Câmara (Scanner)", "Carregar Ficheiro de Imagem"],
        horizontal=True,
    )

    imagem_pedido = None
    if tipo_captura == "Tirar Foto com a Câmara (Scanner)":
      imagem_pedido = st.camera_input("Aponte a câmara para o talão do pedido")
    else:
      imagem_pedido = st.file_uploader(
          "Enviar Imagem do Pedido", type=["png", "jpg", "jpeg"]
      )

    nome_cliente = st.text_input(
        "Nome do Cliente / Destino do Pedido",
        placeholder="Ex: Neriah Comércio",
    )

    if imagem_pedido:
      st.image(imagem_pedido, caption="Imagem do Pedido Capturada", width=350)
      st.success("📸 Imagem escaneada e pronta a processar!")

  st.markdown("<br>", unsafe_allow_html=True)

  with st.container(border=True):
    st.subheader("🛒 2. Adicionar Itens à Lista de Separação")

    if "pedido_temp" not in st.session_state:
      st.session_state.pedido_temp = []

    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
      prod_pedido = st.selectbox(
          "Selecione o Produto", df["Produto"].tolist(), key="p_prod"
      )
    with col_p2:
      qtd_pedido_item = st.number_input(
          "Quantidade Solicitada", min_value=1, step=1, key="p_qtd"
      )

    if st.button("➕ Adicionar Item ao Pedido"):
      st.session_state.pedido_temp.append(
          {"produto": prod_pedido, "qtd": qtd_pedido_item}
      )
      st.success(f"Adicionado: {prod_pedido} ({qtd_pedido_item} un)")

    if st.session_state.pedido_temp:
      st.markdown("#### Itens Atuais no Pedido:")
      for itm in st.session_state.pedido_temp:
        st.write(f"- 📦 **{itm['produto']}**: {itm['qtd']} unidades")

      if st.button("🚀 Finalizar e Criar Pedido Ativo"):
        if nome_cliente:
          id_ped = f"Pedido_{datetime.datetime.now().strftime('%H%M%S')}"
          st.session_state.pedidos_ativos[id_ped] = {
              "cliente": nome_cliente,
              "itens": [
                  {
                      "produto": i["produto"],
                      "qtd_pedida": i["qtd"],
                      "qtd_separada": 0,
                  }
                  for i in st.session_state.pedido_temp
              ],
              "concluido": False,
          }
          st.session_state.pedido_temp = []
          st.success(
              f"Pedido '{id_ped}' criado com sucesso para {nome_cliente}!"
          )
          st.rerun()
        else:
          st.error(
              "Por favor, preencha o nome do cliente antes de finalizar."
          )

  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown("### 📋 3. Check-list de Separação Ativa")

  if not st.session_state.pedidos_ativos:
    st.info("ℹ️ Não existem pedidos ativos no momento.")
  else:
    for id_p, dados_p in st.session_state.pedidos_ativos.items():
      status_txt = (
          "✅ Concluído" if dados_p["concluido"] else "⏳ Em Andamento"
      )

      with st.expander(
          f"📦 {id_p} — Cliente: **{dados_p['cliente']}** [{status_txt}]",
          expanded=not dados_p["concluido"],
      ):
        scan_barras = st.text_input(
            f"🔍 Bipar Código de Barras para Separar ({id_p})",
            key=f"scan_{id_p}",
            placeholder="Passe o leitor ou digite o código...",
        )
        if scan_barras:
          match_prod = df[df["Codigo_Barras"] == scan_barras]
          if not match_prod.empty:
            nome_encontrado = match_prod.iloc[0]["Produto"]
            encontrou = False
            for itm in dados_p["itens"]:
              if itm["produto"] == nome_encontrado:
                encontrou = True
                if itm["qtd_separada"] < itm["qtd_pedida"]:
                  itm["qtd_separada"] += 1
                  st.success(
                      f"✔️ Adicionada 1 unidade de {nome_encontrado}! Progresso:"
                      f" {itm['qtd_separada']}/{itm['qtd_pedida']}"
                  )
                  st.rerun()
                else:
                  st.warning(
                      f"O item {nome_encontrado} já atingiu a quantidade máxima"
                      " pedida!"
                  )
            if not encontrou:
              st.error(
                  f"O produto '{nome_encontrado}' não faz parte deste pedido!"
              )
          else:
            st.error("Código de barras não encontrado no stock!")

        st.markdown("---")
        todos_completos = True
        for idx_i, item in enumerate(dados_p["itens"]):
          prod_nome = item["produto"]
          max_qtd = item["qtd_pedida"]
          atual_qtd = item["qtd_separada"]

          cor_estilo = (
              "color: #28a745; font-weight: bold; background-color: #e8f5e9;"
              " padding: 4px 8px; border-radius: 4px;"
              if atual_qtd >= max_qtd
              else "color: #333;"
          )

          col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
          with col_c1:
            st.markdown(
                f"<span style='{cor_estilo}'>{prod_nome}</span>",
                unsafe_allow_html=True,
            )
          with col_c2:
            st.markdown(
                f"<span style='{cor_estilo}'>Progresso:"
                f" **{atual_qtd}/{max_qtd}**</span>",
                unsafe_allow_html=True,
            )
          with col_c3:
            b_mais = st.button("➕", key=f"mais_{id_p}_{idx_i}")
            b_menos = st.button("➖", key=f"menos_{id_p}_{idx_i}")

            if b_mais and atual_qtd < max_qtd:
              item["qtd_separada"] += 1
              st.rerun()
            if b_menos and atual_qtd > 0:
              item["qtd_separada"] -= 1
              st.rerun()

          if atual_qtd < max_qtd:
            todos_completos = False

        st.markdown("<br>", unsafe_allow_html=True)
        if not todos_completos:
          st.warning(
              "⚠️ **Pedido em andamento:** Existem itens com contagem pendente"
              " de separação."
          )
        else:
          st.success(
              "✨ **Tudo pronto! Todos os itens atingiram a contagem máxima"
              " (Verde).**"
          )
          if not dados_p["concluido"]:
            if st.button(
                f"📥 Confirmar Retirada Automática do Stock ({id_p})",
                key=f"baixa_{id_p}z",
            ):
              erro_stock = False
              for item in dados_p["itens"]:
                p_nome = item["produto"]
                q_sep = item["qtd_pedida"]
                r_idx = df[df["Produto"] == p_nome].index[0]
                if df.loc[r_idx, "Quantidade"] >= q_sep:
                  df.loc[r_idx, "Quantidade"] -= q_sep
                  data_atual = datetime.datetime.now().strftime(
                      "%Y-%m-%d %H:%M"
                  )
                  nova_hist = pd.DataFrame(
                      [[
                          data_atual,
                          st.session_state.username,
                          "Expedição por Pedido",
                          p_nome,
                          q_sep,
                      ]],
                      columns=[
                          "Data",
                          "Utilizador",
                          "Acao",
                          "Item",
                          "Quantidade",
                      ],
                  )
                  st.session_state.historico = pd.concat(
                      [st.session_state.historico, nova_hist], ignore_index=True
                  )
                else:
                  erro_stock = True
                  st.error(f"Stock insuficiente para o item {p_nome}!")

              if not erro_stock:
                dados_p["concluido"] = True
                st.success(
                    "Baixa automática efetuada com sucesso no stock geral!"
                )
                st.rerun()


# --- 5. MENSAGENS & FICHEIROS ---
elif menu.startswith("💬 Mensagens"):
  st.header("💬 Central de Mensagens e Partilha de Ficheiros")
  lista_destinatarios = [
      u
      for u in st.session_state.users.keys()
      if u != st.session_state.username
  ]

  if not lista_destinatarios:
    st.info("Não existem outros utilizadores registados.")
  else:
    destinatario = st.selectbox("Para:", lista_destinatarios)
    texto_msg = st.text_area("Texto / Recado")
    ficheiro_anexado = st.file_uploader(
        "Anexar Ficheiro", type=["pdf", "png", "jpg", "csv", "xlsx", "txt"]
    )

    if st.button("Enviar Mensagem / Ficheiro"):
      if texto_msg.strip() or ficheiro_anexado:
        f_nome = ficheiro_anexado.name if ficheiro_anexado else None
        f_bytes = ficheiro_anexado.getvalue() if ficheiro_anexado else None
        st.session_state.mensagens.append({
            "de": st.session_state.username,
            "para": destinatario,
            "texto": texto_msg,
            "ficheiro_nome": f_nome,
            "ficheiro_bytes": f_bytes,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lida": False,
        })
        st.success("Mensagem enviada com sucesso!")
        st.rerun()
      else:
        st.error("Escreva uma mensagem ou anexe um ficheiro.")

  st.divider()
  st.subheader("Caixa de Entrada")
  minhas_msgs = [
      m
      for m in st.session_state.mensagens
      if m["para"] == st.session_state.username
  ]
  if not minhas_msgs:
    st.info("A sua caixa de entrada está limpa.")
  else:
    for i, m in enumerate(minhas_msgs):
      estado = "📩 [Novo]" if not m["lida"] else "✔️ [Lido]"
      with st.expander(f"{estado} De: {m['de']} em {m['data']}"):
        st.write(m["texto"])
        if m["ficheiro_nome"]:
          st.download_button(
              label=f"📥 Descarregar Ficheiro: {m['ficheiro_nome']}",
              data=m["ficheiro_bytes"],
              file_name=m["ficheiro_nome"],
              key=f"dl_msg_{i}",
          )
        if not m["lida"]:
          if st.button("Marcar como lida", key=f"lida_{i}"):
            m["lida"] = True
            st.rerun()


# --- 6. RELATÓRIOS ---
elif menu == "📊 Romaneios & Relatórios":
  st.header("📊 Emissão de Romaneios Semanais")
  col1, col2 = st.columns(2)
  with col1:
    data_inicio = st.date_input("Início do Período")
  with col2:
    data_fim = st.date_input("Fim do Período")

  if st.button("Gerar Romaneio"):
    st.success(f"Romaneio gerado de {data_inicio} a {data_fim}:")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descarregar Romaneio em CSV",
        data=csv,
        file_name=f"romaneio_{data_inicio}_a_{data_fim}.csv",
        mime="text/csv",
    )


# --- 7. AUDITORIA ---
elif menu == "📜 Histórico de Auditoria":
  st.header("📜 Registo de Atividades")
  if st.session_state.historico.empty:
    st.info("Sem registos de movimentações nesta sessão.")
  else:
    st.dataframe(st.session_state.historico, use_container_width=True)
