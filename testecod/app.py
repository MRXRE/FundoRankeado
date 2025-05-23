import pandas as pd
import streamlit as st

# Carrega o arquivo CSV com tratamento de erros
@st.cache_data
def carregar_dados(caminho_arquivo):
    try:
        return pd.read_csv(caminho_arquivo, encoding="ISO-8859-1", sep=";", on_bad_lines='skip')
    except pd.errors.ParserError:
        st.error("Erro ao ler o CSV. Verifique se o arquivo está no formato correto e se os dados estão bem estruturados.")
        return None
    except Exception as e:
        st.error(f"Erro inesperado ao carregar o arquivo: {e}")
        return None

# Interface
st.set_page_config(page_title="Rendimentos de Fundos", layout="wide")
st.title("📊 Análise de Rendimento Anual de Fundos")
st.markdown("Escolha um fundo abaixo para visualizar os rendimentos anuais:")

# Upload do arquivo
arquivo = st.file_uploader("Envie o arquivo CSV de fundos", type="csv")

if arquivo is not None:
    # Mostra prévia do conteúdo para debug
    conteudo_bruto = arquivo.read()
    st.text(conteudo_bruto[:1000].decode("ISO-8859-1", errors="ignore"))  # Mostra os primeiros 1000 caracteres
    arquivo.seek(0)  # Volta o ponteiro para o início do arquivo

    df = carregar_dados(arquivo)

    if df is not None:
        try:
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

        except KeyError as e:
            st.error(f"Erro de estrutura nos dados: coluna não encontrada - {e}")
    else:
        st.warning("Arquivo inválido. Por favor, envie um CSV estruturado corretamente.")
