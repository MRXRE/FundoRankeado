import pandas as pd
import streamlit as st
from io import BytesIO

@st.cache_data
def carregar_dados(caminho_arquivo):
    try:
        return pd.read_csv(caminho_arquivo, encoding="ISO-8859-1", sep=";")
    except Exception:
        caminho_arquivo.seek(0)
        return pd.read_csv(caminho_arquivo, encoding="utf-8", sep=",")

st.set_page_config(page_title="Rendimentos de Fundos", layout="wide")
st.title("📊 Análise de Rendimento Anual de Fundos")
st.markdown("Escolha um fundo abaixo para visualizar os rendimentos anuais:")

arquivo = st.file_uploader("Envie o arquivo CSV de fundos", type="csv")

if arquivo is not None:
    df = carregar_dados(arquivo)

    # Cálculo de rendimento composto
    df["FATOR"] = 1 + (df["PR_RENTAB_ANO"] / 100)
    fundos = df.groupby(["CNPJ_FUNDO_CLASSE", "DENOM_SOCIAL"])
    produto = fundos["FATOR"].prod().reset_index()
    produto["Rendimento Total (%)"] = (produto["FATOR"] - 1) * 100
    produto = produto.drop(columns=["FATOR"])
    produto = produto.sort_values(by="Rendimento Total (%)", ascending=False)

    st.subheader("🏆 Ranking de Fundos por Rendimento Composto (últimos anos)")
    st.dataframe(
        produto.rename(columns={
            "CNPJ_FUNDO_CLASSE": "CNPJ",
            "DENOM_SOCIAL": "Nome do Fundo"
        }).style.format({"Rendimento Total (%)": "{:.2f}"}),
        use_container_width=True
    )

    # Seleção por CNPJ
    cnpjs = produto["CNPJ_FUNDO_CLASSE"].tolist()
    cnpj_escolhido = st.selectbox("Escolha um fundo para ver os rendimentos anuais:", cnpjs)

    if cnpj_escolhido:
        nome = produto[produto["CNPJ_FUNDO_CLASSE"] == cnpj_escolhido]["DENOM_SOCIAL"].values[0]
        st.markdown(f"**Detalhamento do fundo:** `{cnpj_escolhido}` - **{nome}**")

        detalhes = df[df["CNPJ_FUNDO_CLASSE"] == cnpj_escolhido][["ANO_RENTAB", "PR_RENTAB_ANO"]]
        detalhes = detalhes.sort_values(by="ANO_RENTAB")

        st.table(
            detalhes.rename(columns={
                "ANO_RENTAB": "Ano",
                "PR_RENTAB_ANO": "Rendimento (%)"
            }).style.format({"Rendimento (%)": "{:.2f}"}))

    # Download do CSV com os dados do ranking
    def gerar_csv_para_download(df_resultado):
        output = BytesIO()
        df_formatado = df_resultado.rename(columns={
            "CNPJ_FUNDO_CLASSE": "CNPJ",
            "DENOM_SOCIAL": "Nome do Fundo",
            "Rendimento Total (%)": "Rendimento Total (%)"
        })
        df_formatado.to_csv(output, index=False, encoding="utf-8-sig", sep=";")
        output.seek(0)
        return output

    st.subheader("📥 Baixar Ranking de Fundos")
    csv_download = gerar_csv_para_download(produto)
    st.download_button(
        label="📁 Baixar CSV",
        data=csv_download,
        file_name="ranking_fundos.csv",
        mime="text/csv"
    )
