import pandas as pd
import streamlit as st
import os

# Nome do arquivo para salvar os dados do estoque
DB_FILE = "estoque_data.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        df_inicial = pd.DataFrame(columns=["Código", "Produto", "Categoria", "Quantidade", "Estoque Mínimo", "Preço (R$)"])
        df_inicial.to_csv(DB_FILE, index=False)
        return df_inicial

def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

st.set_page_config(page_title="Controle de Estoque", page_icon="📦", layout="wide")

st.title("📦 Sistema de Controle de Estoque")
st.markdown("Gerencie entradas, saídas e alertas de estoque de qualquer dispositivo.")

df = carregar_dados()

# Menu lateral de navegação
menu = st.sidebar.selectbox("Navegação", ["Painel Geral", "Cadastrar Produto", "Movimentação (Entrada/Saída)"])

if menu == "Painel Geral":
    st.header("📊 Visão Geral do Estoque")
    
    if df.empty:
        st.info("Nenhum produto cadastrado. Utilize o menu lateral para adicionar itens.")
    else:
        # Alerta de estoque baixo
        if "Estoque Mínimo" in df.columns and "Quantidade" in df.columns:
            baixo_estoque = df[df["Quantidade"] <= df["Estoque Mínimo"]]
            if not baixo_estoque.empty:
                st.warning("⚠️ **Atenção!** Os seguintes produtos estão com o estoque igual ou abaixo do mínimo:")
                st.dataframe(baixo_estoque, use_container_width=True)
        
        st.subheader("Inventário Completo")
        st.dataframe(df, use_container_width=True)
        
        # Métricas na tela
        col1, col2 = st.columns(2)
        col1.metric("Total de Produtos Únicos", len(df))
        col2.metric("Volume Total de Itens", int(df["Quantidade"].sum()) if not df.empty else 0)

elif menu == "Cadastrar Produto":
    st.header("➕ Cadastrar Novo Produto")
    
    with st.form("form_cadastro"):
        codigo = st.text_input("Código / SKU")
        nome = st.text_input("Nome do Produto")
        categoria = st.text_input("Categoria")
        quantidade = st.number_input("Quantidade Inicial", min_value=0, step=1)
        estoque_minimo = st.number_input("Estoque Mínimo de Alerta", min_value=0, step=1)
        preco = st.number_input("Preço Unitário (R$)", min_value=0.0, format="%.2f")
        
        submitted = st.form_submit_button("Salvar Produto")
        
        if submitted:
            if not nome or not codigo:
                st.error("Preencha pelo menos o Código e o Nome do produto.")
            elif not df.empty and codigo in df["Código"].astype(str).values:
                st.error(f"Já existe um produto cadastrado com o código '{codigo}'.")
            else:
                novo_dado = {
                    "Código": codigo,
                    "Produto": nome,
                    "Categoria": categoria,
                    "Quantidade": quantidade,
                    "Estoque Mínimo": estoque_minimo,
                    "Preço (R$)": preco
                }
                df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)
                salvar_dados(df)
                st.success(f"Produto '{nome}' cadastrado com sucesso!")

elif menu == "Movimentação (Entrada/Saída)":
    st.header("🔄 Registrar Entrada ou Saída")
    
    if df.empty:
        st.warning("Cadastre produtos primeiro para poder movimentar o estoque.")
    else:
        produto_selecionado = st.selectbox("Selecione o Produto", df["Produto"].values)
        tipo_mov = st.radio("Tipo de Movimentação", ["Entrada (Adicionar)", "Saída (Baixa / Venda)"])
        qtd_mov = st.number_input("Quantidade", min_value=1, step=1)
        
        if st.button("Confirmar Movimentação"):
            idx = df[df["Produto"] == produto_selecionado].index[0]
            qtd_atual = int(df.loc[idx, "Quantidade"])
            
            if "Entrada" in tipo_mov:
                nova_qtd = qtd_atual + int(qtd_mov)
                df.loc[idx, "Quantidade"] = nova_qtd
                salvar_dados(df)
                st.success(f"Entrada registrada! Novo estoque de '{produto_selecionado}': {nova_qtd} unidades.")
            else:
                if qtd_atual < qtd_mov:
                    st.error(f"Estoque insuficiente! Quantidade atual disponível: {qtd_atual} unidades.")
                else:
                    nova_qtd = qtd_atual - int(qtd_mov)
                    df.loc[idx, "Quantidade"] = nova_qtd
                    salvar_dados(df)
                    st.success(f"Saída registrada! Novo estoque de '{produto_selecionado}': {nova_qtd} unidades.")