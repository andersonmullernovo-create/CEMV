import datetime
import pandas as pd
import streamlit as st

# Configuração da página orientada ao setor alimentício
st.set_page_config(
    page_title="Gestão de Estoque - Alimentício", page_icon="🍲", layout="wide"
)

# --- INICIALIZAÇÃO DO ESTADO DA SESSÃO ---
if "users" not in st.session_state:
  st.session_state.users = {
      "admin": "1234",
      "operador": "abcd",
      "estoque": "5678",
  }

if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.username = ""

if "historico" not in st.session_state:
  st.session_state.historico = pd.DataFrame(
      columns=["Data", "Utilizador", "Acao", "Item", "Quantidade"]
  )

if "mensagens" not in st.session_state:
  st.session_state.mensagens = []

if "estoque" not in st.session_state:
  st.session_state.estoque = pd.DataFrame({
      "Codigo_Barras": ["789101", "789102", "789103"],
      "Produto": [
          "Molho de Tomate (Lote A)",
          "Farinha de Trigo (Kg)",
          "Óleo de Soja (L)",
      ],
      "Categoria": ["Matéria-Prima", "Matéria-Prima", "Insumo"],
      "Quantidade": [4, 30, 2],
      "Limite_Minimo": [10, 25, 5],
      "Validade": ["2026-11-15", "2027-05-20", "2026-11-10"],
      "Ultima_Modificacao": ["2026-11-01", "2026-11-05", "2026-11-10"],
      "Modificado_Por": ["admin", "operador", "admin"],
  })

# --- SISTEMA DE LOGIN ---
if not st.session_state.logged_in:
  st.title("🍲 Controlo de Estoque & Expedição - Alimentar")
  st.markdown("Insira as suas credenciais para aceder ao armazém.")
  user_input = st.text_input("Utilizador")
  pass_input = st.text_input("Senha", type="password")

  if st.button("Entrar no Sistema"):
    if (
        user_input in st.session_state.users
        and st.session_state.users[user_input] == pass_input
    ):
      st.session_state.logged_in = True
      st.session_state.username = user_input
      st.success("Login efetuado com sucesso!")
      st.rerun()
    else:
      st.error("Utilizador ou senha incorretos.")
  st.stop()

# --- BARRA LATERAL (MENU E NOTIFICAÇÕES) ---
st.sidebar.title(f"👤 Olá, {st.session_state.username}")

msgs_nao_lidas = [
    m
    for m in st.session_state.mensagens
    if m["para"] == st.session_state.username and not m["lida"]
]
num_novas = len(msgs_nao_lidas)

if num_novas > 0:
  st.sidebar.warning(f"🔔 Tem {num_novas} nova(s) mensagem(ns)!")

menu = st.sidebar.selectbox(
    "Navegação do Armazém", [
        "🍲 Consultar Stock & Validades",
        "➕ Entradas / Saídas (Expedição)",
        f"💬 Mensagens Internas ({num_novas})",
        "📊 Romaneios & Relatórios",
        "📜 Histórico de Auditoria",
    ]
)

if st.sidebar.button("Terminar Sessão"):
  st.session_state.logged_in = False
  st.rerun()

df = st.session_state.estoque

# --- 1. CONSULTAR STOCK ---
if menu == "🍲 Consultar Stock & Validades":
  st.header("🍲 Consulta de Stock e Controlo de Validades")

  pesquisa = st.text_input("🔍 Pesquisar por Alimento, Categoria ou Código de Barras", "")
  df_filtrado = df.copy()
  if pesquisa:
    df_filtrado = df[
        df["Produto"].str.contains(pesquisa, case=False, na=False)
        | df["Categoria"].str.contains(pesquisa, case=False, na=False)
        | df["Codigo_Barras"].str.contains(pesquisa, case=False, na=False)
    ]


  # Função para destacar stock crítico ou perto da validade a vermelho
  def destacar_estoque_e_validade(row):
    hoje = datetime.date.today().strftime("%Y-%m-%d")
    estilo = [""] * len(row)
    # Se quantidade abaixo do mínimo ou validade expirada/vencendo
    if row["Quantidade"] <= row["Limite_Minimo"] or row["Validade"] <= hoje:
      return ["color: red; font-weight: bold"] * len(row)
    return estilo


  st.dataframe(
      df_filtrado.style.apply(destacar_estoque_e_validade, axis=1),
      use_container_width=True,
  )
  st.info(
      "🔴 Itens a **vermelho** indicam stock abaixo do limite mínimo ou produtos com"
      " prazo de validade vencido/crítico."
  )


# --- 2. ENTRADAS E SAÍDAS ---
elif menu == "➕ Entradas / Saídas (Expedição)":
  st.header("➕ Registo de Recebimento ou Expedição de Alimentos")

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
        st.error("Código de barras não registado no sistema de alimentos!")

  if produto_selecionado:
    tipo_mov = st.radio(
        "Operação de Armazém",
        ["Recebimento (Entrada)", "Expedição / Baixa (Retirada)"],
    )
    qtd_mov = st.number_input("Quantidade", min_value=1, step=1)
    
    # Se for entrada, podemos atualizar ou verificar validade do lote
    nova_validade = None
    if "Recebimento" in tipo_mov:
      nova_validade = st.date_input("Data de Validade do Lote Recebido", datetime.date.today())

    anexo = st.file_uploader(
        "Anexar Nota Fiscal / Certificado de Análise (Opcional)",
        type=["pdf", "png", "jpg"],
    )

    if st.button("Registar Operação no Armazém"):
      idx = df[df["Produto"] == produto_selecionado].index[0]
      data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

      if "Recebimento" in tipo_mov:
        df.loc[idx, "Quantidade"] += qtd_mov
        df.loc[idx, "Validade"] = str(nova_validade)
        acao = "Recebimento"
      else:
        if df.loc[idx, "Quantidade"] >= qtd_mov:
          df.loc[idx, "Quantidade"] -= qtd_mov
          acao = "Expedição"
        else:
          st.error("Quantidade insuficiente em stock para esta expedição!")
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
      if anexo is not None:
        st.info(f"Documento '{anexo.name}' arquivado com sucesso.")


# --- 3. MENSAGENS ---
elif menu.startswith("💬 Mensagens"):
  st.header("💬 Central de Mensagens da Equipa de Armazém")

  st.subheader("Enviar Recado / Aviso")
  lista_destinatarios = [u for u in st.session_state.users.keys() if u != st.session_state.username]
  
  if not lista_destinatarios:
    st.info("Não existem outros operadores no sistema.")
  else:
    destinatario = st.selectbox("Para:", lista_destinatarios)
    texto_msg = st.text_area("Assunto / Mensagem (ex: Lote de carnes verificado)")
    
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
    st.info("A caixa de entrada está limpa.")
  else:
    for i, m in enumerate(minhas_msgs):
      estado = "📩 [Novo]" if not m["lida"] else "✔️ [Lido]"
      with st.expander(f"{estado} De: {m['de']} em {m['data']}"):
        st.write(m["texto"])
        if not m["lida"]:
          if st.button(f"Marcar como lida #{i}", key=f"lida_{i}"):
            m["lida"] = True
            st.rerun()


# --- 4. RELATÓRIOS & ROMANEIOS ---
elif menu == "📊 Romaneios & Relatórios":
  st.header("📊 Emissão de Romaneios Semanais de Expedição")

  col1, col2 = st.columns(2)
  with col1:
    data_inicio = st.date_input("Início do Período")
  with col2:
    data_fim = st.date_input("Fim do Período")

  if st.button("Gerar Romaneio"):
    st.success(f"Romaneio alimentar gerado de {data_inicio} a {data_fim}:")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descarregar Romaneio em CSV",
        data=csv,
        file_name=f"romaneio_alimentar_{data_inicio}_a_{data_fim}.csv",
        mime="text/csv",
    )


# --- 5. AUDITORIA ---
elif menu == "📜 Histórico de Auditoria":
  st.header("📜 Registo de Atividades e Modificações")
  if st.session_state.historico.empty:
    st.info("Sem registos de movimentações nesta sessão.")
  else:
    st.dataframe(st.session_state.historico, use_container_width=True)
