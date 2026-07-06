"""
Etapa 4 do pipeline — Dashboard (Streamlit).

Exibe o resultado de todo o pipeline: os livros coletados, o preço por
categoria, e a previsão do modelo (bem avaliado ou não) comparada com
a avaliação real.

Rode: streamlit run dashboard/app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

CSV_PATH = Path(__file__).parent.parent / "dados" / "livros_com_previsoes.csv"

st.set_page_config(page_title="Pipeline — Coleta → Dashboard", page_icon="🔗", layout="wide")


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    return pd.read_csv(CSV_PATH)


if not CSV_PATH.exists():
    st.error(
        "Arquivo de dados não encontrado. Rode, em ordem: "
        "`coleta/coletor.py` (ou use os dados de exemplo) → "
        "`tratamento/tratar_dados.py` → `modelo/aplicar_modelo.py`."
    )
    st.stop()

df = carregar_dados()

st.title("🔗 Pipeline: Coleta → Tratamento → Modelo → Dashboard")
st.caption(
    "Playwright coleta os livros do books.toscrape.com, Pandas trata os dados, "
    "um RandomForestClassifier prevê se o livro será bem avaliado, e este painel exibe tudo."
)

# ----------------------------------------------------------------
# Filtros
# ----------------------------------------------------------------
st.sidebar.header("Filtros")
categorias = st.sidebar.multiselect("Categoria", sorted(df["categoria"].unique()))
faixa_preco = st.sidebar.slider(
    "Faixa de preço (£)", float(df["preco"].min()), float(df["preco"].max()),
    (float(df["preco"].min()), float(df["preco"].max())),
)

df_filtrado = df.copy()
if categorias:
    df_filtrado = df_filtrado[df_filtrado["categoria"].isin(categorias)]
df_filtrado = df_filtrado[
    (df_filtrado["preco"] >= faixa_preco[0]) & (df_filtrado["preco"] <= faixa_preco[1])
]

# ----------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------
acuracia = (df_filtrado["bem_avaliado"] == df_filtrado["previsto_bem_avaliado"]).mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Livros coletados", len(df_filtrado))
col2.metric("Preço médio", f"£{df_filtrado['preco'].mean():.2f}")
col3.metric("% bem avaliados (real)", f"{df_filtrado['bem_avaliado'].mean():.0%}")
col4.metric("Acerto do modelo", f"{acuracia:.0%}")

st.divider()

# ----------------------------------------------------------------
# Gráficos
# ----------------------------------------------------------------
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("Preço por categoria")
    fig_preco = px.box(df_filtrado, x="categoria", y="preco", points="all")
    fig_preco.update_layout(xaxis_title="", yaxis_title="Preço (£)")
    st.plotly_chart(fig_preco, use_container_width=True)

with col_dir:
    st.subheader("Previsão do modelo vs. avaliação real")
    df_filtrado["resultado"] = df_filtrado.apply(
        lambda r: "Acertou" if r["bem_avaliado"] == r["previsto_bem_avaliado"] else "Errou",
        axis=1,
    )
    contagem = df_filtrado["resultado"].value_counts().reset_index()
    contagem.columns = ["resultado", "quantidade"]
    fig_resultado = px.bar(contagem, x="resultado", y="quantidade", color="resultado")
    fig_resultado.update_layout(showlegend=False, xaxis_title="", yaxis_title="Livros")
    st.plotly_chart(fig_resultado, use_container_width=True)

st.subheader("Probabilidade prevista vs. preço")
fig_scatter = px.scatter(
    df_filtrado,
    x="preco",
    y="probabilidade_bem_avaliado",
    color=df_filtrado["bem_avaliado"].map({1: "Bem avaliado", 0: "Não bem avaliado"}),
    hover_data=["titulo", "categoria", "estrelas"],
    labels={"color": "Avaliação real"},
)
fig_scatter.update_layout(xaxis_title="Preço (£)", yaxis_title="Probabilidade prevista")
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ----------------------------------------------------------------
# Tabela detalhada
# ----------------------------------------------------------------
st.subheader("Dados detalhados")
st.dataframe(
    df_filtrado[
        ["titulo", "categoria", "preco", "estrelas", "bem_avaliado", "probabilidade_bem_avaliado", "previsto_bem_avaliado"]
    ],
    use_container_width=True,
    hide_index=True,
)
