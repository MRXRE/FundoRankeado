import pandas as pd
import streamlit as st
from io import BytesIO

@st.cache_data
def carregar_dados(caminho_arquivo):
    return pd.read_csv(caminho_arquivo, encoding="ISO-8859-1")

st.set_page_config(page_title="Rendimentos de Fundos", layout="wide")
st.title("📊 Análise de Rendimento Anual de Fundos")
st.markdown("Escolha um fundo abaixo para visualizar os rendimentos anuais:")

arquivo = st.file_uploader("Envie o arquivo CSV de fundos", type="csv")

if arquivo is not None:
    df = carregar_dados(arquivo)

    # Cálculo do rendimento composto acumulado por fundo
    fundos = df.groupby(["CNPJ_FUNDO_CLASSE", "DENOM_SOCIAL"])
    somas = fundos["PR_RENTAB_ANO"].apply(lambda x: (x / 100 + 1).prod() - 1).reset_index()
    somas["PR_RENTAB_ANO"] = somas["PR_RENTAB_ANO"] * 100  # Convertendo para porcentagem
    somas = somas.sort_values(by="PR_RENTAB_ANO", ascending=False)

    # Formata tabela para exibição
    tabela_formatada = somas.rename(columns={
        "CNPJ_FUNDO_CLASSE": "CNPJ",
        "DENOM_SOCIAL": "Nome do Fundo",
        "PR_RENTAB_ANO": "Rendimento Total (%)"
    })

    st.subheader("🏆 Ranking de Fundos por Rendimento Total (últimos 4 anos)")
    st.dataframe(tabela_formatada.style.format({"Rendimento Total (%)": "{:.2f}"}), use_container_width=True)

    # Detalhamento de um fundo específico
    st.subheader("🔎 Detalhar Rendimento por Fundo")

    # Combina nome e CNPJ para facilitar escolha
    tabela_formatada["Identificação"] = tabela_formatada["Nome do Fundo"] + " — " + tabela_formatada["CNPJ"]
    identificacoes = tabela_formatada["Identificação"].tolist()
    identificacao_escolhida = st.selectbox("Escolha um fundo:", identificacoes)

    if identificacao_escolhida:
        cnpj_escolhido = identificacao_escolhida.split(" — ")[1]
        nome_escolhido = identificacao_escolhida.split(" — ")[0]
        detalhes = df[df["CNPJ_FUNDO_CLASSE"] == cnpj_escolhido][["ANO_RENTAB", "PR_RENTAB_ANO"]]
        detalhes = detalhes.sort_values(by="ANO_RENTAB")

        st.markdown(f"**Detalhamento do fundo:** `{nome_escolhido}` (`{cnpj_escolhido}`)")
        st.table(detalhes.rename(columns={
            "ANO_RENTAB": "Ano",
            "PR_RENTAB_ANO": "Rendimento (%)"
        }).style.format({"Rendimento (%)": "{:.2f}"}))

    # Botão de download no final da página
    st.subheader("📥 Baixar Tabela Completa")
    csv = tabela_formatada[["Nome do Fundo", "CNPJ", "Rendimento Total (%)"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Clique aqui para baixar o ranking como CSV",
        data=csv,
        file_name="ranking_fundos.csv",
        mime="text/csv"
    )
