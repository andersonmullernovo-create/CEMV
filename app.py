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
