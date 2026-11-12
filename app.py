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
      "admin": {"senha": "1234", "perfil": "Administrador"},
      "operador": {"senha": "abcd", "perfil": "Operador"},
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
          "Molho de Tomate (Lote A)",
          "Farinha de Trigo (Kg)",
          "Óleo de Soja (L)",
      ],
      "Setor": ["Secos e Molhados", "Secos e Molhados", "Câmara Fria"],
      "Categoria": ["Matéria-Prima", "Matéria-Prima", "Insumo"],
      "Quantidade": [4, 30, 2],
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
  st.title("Controle de Estoque & Expedição")
  st.markdown("Insira as suas credenciais para aceder ao armazém.")
  user_input = st.text_input("Usuário")
  pass_input = st.text_input("Senha", type="password")

  if st.button("Entrar"):
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

# --- BARRA LATERAL (MENU E PERFIL) ---
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
    "🍲 Consultar Estoque & Setores",
    "➕ Entradas / Saídas (Expedição)",
    "📋 Gestão de Pedidos & Check-list",
    f"💬 Mensagens Internas ({num_novas})",
    "📊 Romaneios & Relatórios",
    "📜 Histórico de Auditoria",
]

if st.session_state.perfil == "Administrador":
  opcoes_menu.insert(1, "⚙️ Painel do Administrador")

menu = st.sidebar.selectbox("Navegação do Armazém", opcoes_menu)

if st.sidebar.button("Terminar Sessão"):
  st.session_state.logged_in = False
  st.rerun()

df = st.session_state.estoque

# --- 1. PAINEL DO ADMINISTRADOR (Utilizadores, Setores & Visual) ---
if menu == "⚙️ Painel do Administrador":
  st.header("⚙️ Painel de Controlo do Administrador")

  col_adm1, col_adm2 = st.columns(2)

  with col_adm1:
    st.subheader("👥 Criar Novo Utilizador")
    novo_user = st.text_input("Nome do Novo Utilizador")
    nova_senha = st.text_input("Senha do Utilizador", type="password")
    novo_perfil = st.selectbox("Perfil de Acesso", ["Operador", "Administrador"])

    if st.button("Registar Utilizador"):
      if novo_user and nova_senha:
        if novo_user in st.session_state.users:
          st.error("Este utilizador já existe!")
        else:
          st.session_state.users[novo_user] = {
              "senha": nova_senha,
              "perfil": novo_perfil,
          }
          st.success(f"Utilizador '{novo_user}' criado com sucesso!")
      else:
        st.error("Preencha todos os campos do utilizador.")

    st.divider()
    st.subheader("Utilizadores Atuais")
    for u, dados in st.session_state.users.items():
      st.write(f"- **{u}** ({dados['perfil']})")

  with col_adm2:
    st.subheader("🏢 Criar Novo Setor")
    novo_setor = st.text_input("Nome do Setor (ex: Câmara de Congelados)")

    if st.button("Adicionar Setor"):
      if novo_setor:
        if novo_setor in st.session_state.setores:
          st.error("Este setor já existe!")
        else:
          st.session_state.setores.append(novo_setor)
          st.success(f"Setor '{novo_setor}' criado com sucesso!")
      else:
        st.error("Insira o nome do setor.")

    st.divider()
    st.subheader("Setores Existentes")
    for s in st.session_state.setores:
      st.write(f"- 🏭 {s}")

  st.divider()
  st.subheader("🎨 Personalização Visual do Sistema")
  tamanho_escolhido = st.selectbox(
      "Tamanho da Fonte", ["14px", "16px", "18px"], index=1
  )
  cor_texto_escolhida = st.color_picker("Cor Principal do Texto", cfg["cor_texto"])
  cor_tabela_escolhida = st.color_picker(
      "Cor de Fundo das Tabelas", cfg["cor_fundo_tabela"]
  )

  if st.button("Aplicar Personalização Visual"):
    st.session_state.config_visual["tamanho_fonte"] = tamanho_escolhido
    st.session_state.config_visual["cor_texto"] = cor_texto_escolhida
    st.session_state.config_visual["cor_fundo_tabela"] = cor_tabela_escolhida
    st.success("Estilo visual atualizado com sucesso!")
    st.rerun()

  st.divider()
  st.subheader("🗑️ Eliminar Item do Stock")
  produto_a_excluir = st.selectbox(
      "Selecione o produto a remover permanentemente",
      df["Produto"].tolist(),
      key="excluir_prod",
  )

  if st.button("❌ Confirmar Eliminação do Produto"):
    idx_excluir = df[df["Produto"] == produto_a_excluir].index[0]
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    nova_hist = pd.DataFrame(
        [[data_atual, st.session_state.username, "Eliminação de Produto", produto_a_excluir, 0]],
        columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
    )
    st.session_state.historico = pd.concat(
        [st.session_state.historico, nova_hist], ignore_index=True
    )
    st.session_state.estoque = df.drop(idx_excluir).reset_index(drop=True)
    st.success(f"O produto '{produto_a_excluir}' foi eliminado do stock com sucesso!")
    st.rerun()


# --- 2. CONSULTAR STOCK & SETORES ---
elif menu == "🍲 Consultar Stock & Setores":
  st.header("🍲 Consulta Geral de Stock e Visão por Setor")

  setor_filtro = st.selectbox(
      "Filtrar por Setor de Armazenamento", ["Todos os Setores"] + st.session_state.setores
  )
  pesquisa = st.text_input("🔍 Pesquisar por Alimento ou Código de Barras", "")

  df_filtrado = df.copy()
  if setor_filtro != "Todos os Setores":
    df_filtrado = df_filtrado[df_filtrado["Setor"] == setor_filtro]

  if pesquisa:
    df_filtrado = df_filtrado[
        df_filtrado["Produto"].str.contains(pesquisa, case=False, na=False)
        | df_filtrado["Codigo_Barras"].str.contains(pesquisa, case=False, na=False)
    ]


  def destacar_estoque_e_validade(row):
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    if row["Quantidade"] <= row["Limite_Minimo"] or row["Validade"] <= hoje:
      return ["color: red; font-weight: bold"] * len(row)
    return [""] * len(row)


  st.dataframe(
      df_filtrado.style.apply(destacar_estoque_e_validade, axis=1),
      use_container_width=True,
  )
  st.info("🔴 Itens a **vermelho** indicam stock crítico ou validade vencida/próxima.")


# --- 3. ENTRADAS E SAÍDAS (Com Cadastro Manual Direto) ---
elif menu == "➕ Entradas / Saídas (Expedição)":
  st.header("➕ Registo de Recebimento ou Expedição de Alimentos")

  # Opção de cadastrar item novo diretamente na tela de entradas
  cadastrar_novo = st.checkbox("➕ O produto não existe? Cadastrar novo item manualmente")

  if cadastrar_novo:
    st.subheader("Registar Novo Item no Armazém")
    novo_prod_nome = st.text_input("Nome do Novo Alimento / Insumo")
    novo_prod_cod = st.text_input("Código de Barras do Novo Item")
    novo_prod_setor = st.selectbox("Setor de Armazenamento", st.session_state.setores)
    novo_limite = st.number_input("Limite Mínimo de Stock", min_value=1, value=10)

    if st.button("Guardar Novo Item"):
      if novo_prod_nome and novo_prod_cod:
        nova_linha = pd.DataFrame({
            "Codigo_Barras": [novo_prod_cod],
            "Produto": [novo_prod_nome],
            "Setor": [novo_prod_setor],
            "Categoria": ["Geral"],
            "Quantidade": [0],
            "Limite_Minimo": [novo_limite],
            "Validade": [datetime.date.today().strftime("%Y-%m-%d")],
            "Ultima_Modificacao": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Modificado_Por": [st.session_state.username],
        })
        st.session_state.estoque = pd.concat(
            [st.session_state.estoque, nova_linha], ignore_index=True
        )
        st.success(f"Produto '{novo_prod_nome}' criado com sucesso! Já pode selecionar abaixo.")
        st.rerun()
      else:
        st.error("Preencha o nome e o código de barras.")
    st.divider()

  modo_entrada = st.radio(
      "Método de Identificação", ["Selecionar na Lista", "Digitar Código de Barras"]
  )

  produto_selecionado = None
  if modo_entrada == "Selecionar na Lista":
    produto_selecionado = st.selectbox("Selecione o Alimento / Insumo", df["Produto"].tolist())
  else:
    cod_leitor = st.text_input("Aponte o leitor ou digite o Código de Barras")
    if cod_leitor:
      match = df[df["Codigo_Barras"] == cod_leitor]
      if not match.empty:
        produto_selecionado = match.iloc[0]["Produto"]
        st.success(f"Item detetado: **{produto_selecionado}**")
      else:
        st.error("Código de barras não registado!")

  if produto_selecionado:
    tipo_mov = st.radio(
        "Operação de Armazém",
        ["Recebimento (Entrada)", "Expedição / Baixa (Retirada)"],
    )
    qtd_mov = st.number_input("Quantidade", min_value=1, step=1)

    nova_validade = None
    if "Recebimento" in tipo_mov:
      nova_validade = st.date_input("Data de Validade do Lote", datetime.date.today())

    anexo = st.file_uploader(
        "Anexar Nota Fiscal / Certificado (Opcional)", type=["pdf", "png", "jpg"]
    )

    if st.button("Registar Operação"):
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
          st.error("Quantidade insuficiente em stock!")
          st.stop()

      df.loc[idx, "Ultima_Modificacao"] = data_atual
      df.loc[idx, "Modificado_Por"] = st.session_state.username

      nova_hist = pd.DataFrame(
          [[data_atual, st.session_state.username, acao, produto_selecionado, qtd_mov]],
          columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
      )
      st.session_state.historico = pd.concat(
          [st.session_state.historico, nova_hist], ignore_index=True
      )

      st.success(f"Operação de {acao} registada com sucesso!")


# --- 4. GESTÃO DE PEDIDOS & CHECK-LIST ---
elif menu == "📋 Gestão de Pedidos & Check-list":
  st.header("📋 Gestão de Pedidos e Check-list de Separação")

  st.subheader("1. Carregar Pedido por Imagem")
  nome_cliente = st.text_input("Nome do Cliente / Destino do Pedido")
  imagem_pedido = st.file_uploader(
      "📸 Enviar Imagem do Pedido", type=["png", "jpg", "jpeg"]
  )

  if imagem_pedido:
    st.image(imagem_pedido, caption="Imagem do Pedido Carregada", width=300)
    st.info("💡 Imagem escaneada com sucesso. Adicione os itens abaixo.")

  st.markdown("---")
  st.subheader("2. Adicionar Itens ao Pedido")

  if "pedido_temp" not in st.session_state:
    st.session_state.pedido_temp = []

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    prod_pedido = st.selectbox("Produto", df["Produto"].tolist(), key="p_prod")
  with col_p2:
    qtd_pedido_item = st.number_input("Quantidade Solicitada", min_value=1, step=1, key="p_qtd")

  if st.button("Adicionar Item à Lista de Separação"):
    st.session_state.pedido_temp.append({"produto": prod_pedido, "qtd": qtd_pedido_item})
    st.success(f"Adicionado: {prod_pedido} ({qtd_pedido_item} un)")

  if st.session_state.pedido_temp:
    st.write("### Itens atuais no Pedido:")
    for item_p in st.session_state.pedido_temp:
      st.write(f"- {item_p['produto']}: **{item_p['qtd']} unidades**")

    if st.button("Finalizar e Criar Pedido Ativo"):
      if nome_cliente:
        id_ped = f"Pedido_{datetime.datetime.now().strftime('%H%M%S')}"
        st.session_state.pedidos_ativos[id_ped] = {
            "cliente": nome_cliente,
            "itens": [
                {"produto": i["produto"], "qtd_pedida": i["qtd"], "separado": False}
                for i in st.session_state.pedido_temp
            ],
            "concluido": False,
        }
        st.session_state.pedido_temp = []
        st.success(f"Pedido '{id_ped}' criado com sucesso para {nome_cliente}!")
        st.rerun()
      else:
        st.error("Insira o nome do cliente/destino.")

  st.divider()
  st.subheader("3. Check-list e Retirada Automática")

  if not st.session_state.pedidos_ativos:
    st.info("Não existem pedidos ativos no momento.")
  else:
    for id_p, dados_p in st.session_state.pedidos_ativos.items():
      status_txt = "✅ Concluído" if dados_p["concluido"] else "⏳ Em Separação (Pendente)"
      with st.expander(f"📦 {id_p} - Cliente: {dados_p['cliente']} [{status_txt}]"):

        todos_separados = True
        for idx_i, item in enumerate(dados_p["itens"]):
          prod_nome = item["produto"]
          qtd_ped = item["qtd_pedida"]
          sep_status = item["separado"]

          checked = st.checkbox(
              f"Separar {qtd_ped}x **{prod_nome}**",
              value=sep_status,
              key=f"check_{id_p}_{idx_i}",
          )

          if checked != sep_status:
            dados_p["itens"][idx_i]["separado"] = checked
            st.rerun()

          if not checked:
            todos_separados = False

        if not todos_separados:
          st.warning("⚠️ **Pedido incompleto:** Faltam itens por separar e retirar do stock.")
        else:
          st.success("✨ **Pedido totalmente separado!** Pronto para dar baixa automática.")
          if not dados_p["concluido"]:
            if st.button(f"Confirmar Retirada Automática ({id_p})", key=f"btn_baixa_{id_p}"):
              erro_baixa = False
              for item in dados_p["itens"]:
                p_nome = item["produto"]
                q_ped = item["qtd_pedida"]
                row_idx = df[df["Produto"] == p_nome].index[0]

                if df.loc[row_idx, "Quantidade"] >= q_ped:
                  df.loc[row_idx, "Quantidade"] -= q_ped
                  data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                  nova_hist = pd.DataFrame(
                      [[data_atual, st.session_state.username, "Expedição por Pedido", p_nome, q_ped]],
                      columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"],
                  )
                  st.session_state.historico = pd.concat(
                      [st.session_state.historico, nova_hist], ignore_index=True
                  )
                else:
                  erro_baixa = True
                  st.error(f"Stock insuficiente para o item {p_nome}!")

              if not erro_baixa:
                dados_p["concluido"] = True
                st.success("Baixa automática realizada com sucesso!")
                st.rerun()


# --- 5. MENSAGENS ---
elif menu.startswith("💬 Mensagens"):
  st.header("💬 Central de Mensagens da Equipa")
  st.subheader("Enviar Recado / Aviso")
  lista_destinatarios = [u for u in st.session_state.users.keys() if u != st.session_state.username]

  if not lista_destinatarios:
    st.info("Não existem outros utilizadores registados.")
  else:
    destinatario = st.selectbox("Para:", lista_destinatarios)
    texto_msg = st.text_area("Mensagem")

    if st.button("Enviar Mensagem"):
      if texto_msg.strip():
        nova_m = {
            "de": st.session_state.username,
            "para": destinatario,
            "texto": texto_msg,
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "lida": False,
        }
        st.session_state.mensagens.append(nova_m)
        st.success("Mensagem enviada!")
      else:
        st.error("Escreva uma mensagem válida.")

  st.divider()
  st.subheader("Caixa de Entrada")
  minhas_msgs = [m for m in st.session_state.mensagens if m["para"] == st.session_state.username]

  if not minhas_msgs:
    st.info("A sua caixa de entrada está limpa.")
  else:
    for i, m in enumerate(minhas_msgs):
      estado = "📩 [Novo]" if not m["lida"] else "✔️ [Lido]"
      with st.expander(f"{estado} De: {m['de']} em {m['data']}"):
        st.write(m["texto"])
        if not m["lida"]:
          if st.button(f"Marcar como lida #{i}", key=f"lida_{i}"):
            m["lida"] = True
            st.rerun()


# --- 6. RELATÓRIOS & ROMANEIOS ---
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
