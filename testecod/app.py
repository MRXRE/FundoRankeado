import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados(caminho_arquivo):
    return pd.read_csv(caminho_arquivo, encoding="ISO-8859-1")

st.set_page_config(page_title="Rendimentos de Fundos", layout="wide")
st.title("📊 Análise de Rendimento Anual de Fundos")
st.markdown("Escolha um fundo abaixo para visualizar os rendimentos anuais:")

arquivo = st.file_uploader("Envie o arquivo CSV de fundos", type="csv")

if arquivo is not None:
    df = carregar_dados(arquivo)

    fundos = df.groupby(["CNPJ_FUNDO_CLASSE", "DENOM_SOCIAL"])
    somas = fundos["PR_RENTAB_ANO"].sum().reset_index()
    somas = somas.sort_values(by="PR_RENTAB_ANO", ascending=False)

    st.subheader("🏆 Ranking de Fundos por Rendimento Total (últimos 4 anos)")
    st.dataframe(
        somas.rename(columns={
            "CNPJ_FUNDO_CLASSE": "CNPJ",
            "DENOM_SOCIAL": "Nome do Fundo",
            "PR_RENTAB_ANO": "Rendimento Total (%)"
        }).style.format({"Rendimento Total (%)": "{:.2f}"}),
        use_container_width=True
    )

    st.subheader("🔎 Detalhar Rendimento por Fundo")
    cnpjs = somas["CNPJ_FUNDO_CLASSE"].tolist()
    cnpj_escolhido = st.selectbox("Escolha um CNPJ para ver os detalhes:", cnpjs)

    if cnpj_escolhido:
        nome = somas[somas["CNPJ_FUNDO_CLASSE"] == cnpj_escolhido]["DENOM_SOCIAL"].values[0]
        detalhes = df[df["CNPJ_FUNDO_CLASSE"] == cnpj_escolhido][["ANO_RENTAB", "PR_RENTAB_ANO"]]
        detalhes = detalhes.sort_values(by="ANO_RENTAB")

        st.markdown(f"**Detalhamento do fundo:** `{nome}`")
        st.table(detalhes.rename(columns={
            "ANO_RENTAB": "Ano",
            "PR_RENTAB_ANO": "Rendimento (%)"
        }).style.format({"Rendimento (%)": "{:.2f}"}))
