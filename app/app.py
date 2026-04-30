import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path 
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import geobr
import geopandas as gpd
import json
import math
import streamlit.components.v1 as components


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "processed" / "empresas_sp.duckdb"


st.set_page_config(
    page_title="Empresas e Desenvolvimento em SP",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def run_query(query: str):
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(query).df()
    con.close()
    return df

@st.cache_data
def carregar_geografia():
    sp_geo = geobr.read_municipality(code_muni="SP", year=2024)
    sp_geo["code_muni"] = sp_geo["code_muni"].astype(int).astype(str)
    sp_geo = sp_geo.to_crs(epsg=4326)
    return sp_geo

def classificar_ipdm(valor):
    if valor <= 0.500:
        return "Baixa"
    elif valor <= 0.550:
        return "Média"
    elif valor <= 0.600:
        return "Alta"
    else:
        return "Muito alta"


# =========================
# CARREGA DADOS
# =========================

df = run_query("""
    SELECT 
        v.*,
        i.municipio
    FROM vw_municipios_analise v
    LEFT JOIN ipdm_municipio i
        ON v.cod_munibge = i.cod_munibge
""")

sp_geo = carregar_geografia()



df["cod_munibge"] = df["cod_munibge"].astype(str)

geo_final = sp_geo.merge(
    df,
    left_on="code_muni",
    right_on="cod_munibge",
    how="inner"
)

geo_final["id_mapa"] = geo_final.index.astype(str)
geo_final["grupo_ipdm"] = geo_final["ipdm_total"].apply(classificar_ipdm)

colunas_numericas = [
    "ipdm_total", "riqueza", "escolaridade", "longevidade",
    "populacao", "total_empresas", "empresas_por_1000_hab",
    "pct_micro", "pct_pequena", "pct_demais", "pct_mei",
]
for col in colunas_numericas:
    geo_final[col] = pd.to_numeric(geo_final[col], errors="coerce")






# =========================
# TÍTULO
# =========================

st.title("📊 Estrutura Empresarial e Desenvolvimento Municipal de São Paulo")
st.caption("← Abra o menu lateral para entender o dashboard, as fontes e como navegar.")


# =========================
# BIG NUMBERS
# =========================



total_municipios = df["cod_munibge"].nunique()
populacao_total = df["populacao"].sum()
total_empresas_metric = df["total_empresas"].sum()
densidade_media = df["empresas_por_1000_hab"].mean()
ipdm_medio = df["ipdm_total"].mean()
media_mei_municipio = df["total_mei"].sum() / total_municipios
distribuicao_porte = {
    "Microempresa": df["total_micro"].sum(),
    "Pequena": df["total_pequena"].sum(),
    "Média/Grande": df["total_demais"].sum(),
}

# ordena do maior para o menor (melhor leitura)
distribuicao_porte = dict(
    sorted(distribuicao_porte.items(), key=lambda x: x[1], reverse=True)
)

total_empresas = sum(distribuicao_porte.values())

ordem_ipdm = ["Muito alta", "Alta", "Média", "Baixa"]

distribuicao_ipdm = (
    geo_final["grupo_ipdm"]
    .value_counts()
    .reindex(ordem_ipdm)
    .fillna(0)
    .astype(int)
)

total_municipios = distribuicao_ipdm.sum()


ordem_ipdm = ["Muito alta", "Alta", "Média", "Baixa"]

distribuicao_ipdm = (
    geo_final["grupo_ipdm"]
    .value_counts()
    .reindex(ordem_ipdm)
    .fillna(0)
    .astype(int)
)

total_grupos_ipdm = distribuicao_ipdm.sum()


distribuicao_porte = {
    "Microempresa": df["total_micro"].sum(),
    "Pequena": df["total_pequena"].sum(),
    "Média/Grande": df["total_demais"].sum(),
}

distribuicao_porte = dict(
    sorted(distribuicao_porte.items(), key=lambda x: x[1], reverse=True)
)

total_porte = sum(distribuicao_porte.values())



def card_metrica(label, value, caption=None, help_text=None):
    st.metric(label=label, value=value, help=help_text)
    if caption:
        st.caption(caption)


def card_distribuicao(titulo, distribuicao, total):
    st.markdown(f"**{titulo}**")
    for nome, qtd in distribuicao.items():
        percentual = qtd / total if total > 0 else 0
        # Título e percentual na mesma linha
        st.markdown(f"**{nome}** &nbsp; :green[{percentual:.1%}]", unsafe_allow_html=True)
        st.progress(percentual)
    
def card_distribuicao(titulo, distribuicao, total):
    st.markdown(f"**{titulo}**")
    for nome, qtd in distribuicao.items():
        percentual = qtd / total if total > 0 else 0
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="min-width: 110px; font-size: 13px; font-weight: 600; color: #e0e0e0;">{nome}</span>
                <div style="flex: 1; background-color: #2c2c2c; border-radius: 4px; height: 8px;">
                    <div style="width: {percentual*100:.1f}%; background-color: #4C9BE8; border-radius: 4px; height: 8px;"></div>
                </div>
                <span style="min-width: 50px; font-size: 13px; color: #00CC96; text-align: right;">{percentual:.1%}</span>
            </div>
            """,
            unsafe_allow_html=True
        )






























def card_distribuicao(titulo, distribuicao, total):
    st.markdown(f"**{titulo}**")
    for nome, qtd in distribuicao.items():
        percentual = qtd / total if total > 0 else 0
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span style="min-width: 90px; font-size: 13px; font-weight: 600; color: #e0e0e0;">{nome}</span>
                <div style="flex: 1; background-color: #2c2c2c; border-radius: 4px; height: 8px;">
                    <div style="width: {percentual*100:.1f}%; background-color: #4C9BE8; border-radius: 4px; height: 8px;"></div>
                </div>
                <span style="min-width: 40px; font-size: 13px; color: #00CC96; text-align: right;">{percentual:.1%}</span>
            </div>
            """,
            unsafe_allow_html=True
        )


# Distribuição porte + MEI separado
total_mei = df["total_mei"].sum()
pct_mei = total_mei / total_porte

distribuicao_porte_display = {**distribuicao_porte, "── MEI (regime)": total_mei}
total_porte_com_mei = total_porte  # MEI já está dentro de micro, então mantemos o total


sec1, sec2, sec3 = st.columns([1, 2, 2])

# =========================
# 1ª SEÇÃO: TERRITÓRIO
# =========================
with sec1:
    with st.container(border=True, height=200):
        st.markdown(f"##### 🗺️  {populacao_total/1_000_000:.1f} milhões de hab. nos {total_municipios} municípios de SP")
        st.caption("📁 Fontes: SEADE — Painel de Empresas (2026) e IPDM (2024); IBGE — Censo Demográfico (2022).")

# =========================
# 2ª SEÇÃO: EMPRESAS
# =========================

with sec2:
    with st.container(border=True, height=200):
        col_emp_metricas, col_emp_dist = st.columns([1, 2])

        with col_emp_metricas:
            st.metric(
                label="💼 Total de Empresas",
                value=f"{total_empresas_metric/1_000_000:.1f} mi",
            )
            st.caption(f"Densidade média: {densidade_media:.1f} empresas por 1.000 hab.")

        with col_emp_dist:
            st.markdown("**Estrutura empresarial por porte**")
            for nome, qtd in distribuicao_porte.items():
                percentual = qtd / total_porte
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                        <span style="min-width: 90px; font-size: 13px; font-weight: 600; color: #e0e0e0;">{nome}</span>
                        <div style="flex: 1; background-color: #2c2c2c; border-radius: 4px; height: 8px;">
                            <div style="width: {percentual*100:.1f}%; background-color: #4C9BE8; border-radius: 4px; height: 8px;"></div>
                        </div>
                        <span style="min-width: 40px; font-size: 13px; color: #00CC96; text-align: right;">{percentual:.1%}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Separador + MEI
            st.markdown(
                f"""
                <div style="border-top: 1px solid #333; margin: 8px 0;"></div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="min-width: 90px; font-size: 13px; font-weight: 600; color: #aaa;">MEI (regime)</span>
                    <div style="flex: 1; background-color: #2c2c2c; border-radius: 4px; height: 8px;">
                        <div style="width: {pct_mei*100:.1f}%; background-color: #FF6B6B; border-radius: 4px; height: 8px;"></div>
                    </div>
                    <span style="min-width: 40px; font-size: 13px; color: #FF6B6B; text-align: right;">{pct_mei:.1%}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# 3ª SEÇÃO: DESENVOLVIMENTO
# =========================
help_ipdm = """
O IPDM (Índice Paulista de Desenvolvimento Municipal) é um indicador criado pela Fundação SEADE para medir o desenvolvimento dos 645 municípios paulistas — funcionando de forma similar ao IDH, mas com foco no estado de São Paulo e uso pela gestão pública estadual.

Varia de 0 a 1 e é composto pela média de três dimensões:

- Riqueza: PIB per capita, renda dos trabalhadores formais e consumo de energia elétrica.
- Longevidade: taxas de mortalidade infantil, perinatal e de adultos.
- Escolaridade: acesso à creche, proficiência em português e matemática e distorção idade-série no ensino médio.

Os municípios são classificados em quatro grupos: Muito Alta (> 0,600), Alta (0,550–0,600), Média (0,500–0,550) e Baixa (≤ 0,500).

Fonte: Fundação SEADE — dadosabertos.sp.gov.br
"""
with sec3:
    with st.container(border=True, height=200):
        col_ipdm_metricas, col_ipdm_dist = st.columns([1, 2])

        with col_ipdm_metricas:
            st.metric(
                label="📈 IPDM Médio",
                value=f"{ipdm_medio:.3f}",
                help=help_ipdm
            )
            st.caption(f"Média dos {total_municipios} municípios.")

        with col_ipdm_dist:
            st.markdown("**Municípios por nível de IPDM**")
            for grupo, qtd in distribuicao_ipdm.items():
                percentual = qtd / total_grupos_ipdm
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                        <span style="min-width: 70px; font-size: 13px; font-weight: 600; color: #e0e0e0;">{grupo}</span>
                        <div style="flex: 1; background-color: #2c2c2c; border-radius: 4px; height: 8px;">
                            <div style="width: {percentual*100:.1f}%; background-color: #4C9BE8; border-radius: 4px; height: 8px;"></div>
                        </div>
                        <span style="min-width: 40px; font-size: 13px; color: #00CC96; text-align: right;">{percentual:.1%}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
# =========================
# PREPARA DADOS SCATTER
# =========================

variaveis_scatter = {
    "% MEI": "pct_mei",
    "IPDM total": "ipdm_total",
    "Escolaridade": "escolaridade",
    "Longevidade": "longevidade",
    "Riqueza": "riqueza",
    "População": "populacao",
    "Total de empresas": "total_empresas",
    "Densidade empresarial": "empresas_por_1000_hab",
    "% Microempresas": "pct_micro",
    "% Pequenas empresas": "pct_pequena",
    "% Demais empresas": "pct_demais",
}

df_scatter = df.copy()
df_scatter["grupo_ipdm"] = df_scatter["ipdm_total"].apply(classificar_ipdm)
for col in variaveis_scatter.values():
    df_scatter[col] = pd.to_numeric(df_scatter[col], errors="coerce")

interpretacoes = {
    ("% MEI", "IPDM total"): "Correlação de -0,38: municípios com mais MEIs tendem a ter menor desenvolvimento. A relação pode refletir economias locais menos diversificadas, mas vale lembrar que o inverso também é possível — municípios menos desenvolvidos oferecem menos espaço para negócios maiores.",

    ("% MEI", "Escolaridade"): "Correlação de -0,36: onde há mais MEIs, a escolaridade tende a ser menor. Populações com menos acesso à educação formal tendem a encontrar no empreendedorismo individual uma das principais alternativas de renda.",

    ("% MEI", "Longevidade"): "Correlação de -0,19: associação fraca. A proporção de MEIs tem pouca relação com a expectativa de vida — longevidade parece depender mais de fatores como saúde pública e saneamento.",

    ("% MEI", "Riqueza"): "Correlação de -0,17: associação fraca. Municípios com mais MEIs tendem a ter levemente menos riqueza per capita, mas a relação é tênue e influenciada por muitos outros fatores.",

    ("% MEI", "População"): "Correlação de 0,01: sem associação. O tamanho do município não está relacionado à proporção de MEIs.",

    ("% MEI", "Total de empresas"): "Correlação de -0,00: sem associação. O volume total de empresas não determina a participação dos MEIs na economia local.",

    ("% MEI", "Densidade empresarial"): "Correlação de -0,10: associação muito fraca. Municípios com mais empresas por habitante tendem a ter levemente menos MEIs proporcionalmente.",

    ("% MEI", "% Microempresas"): "Correlação de 0,19: associação fraca positiva. Municípios com mais MEIs também tendem a ter mais microempresas — ambos convivem em economias locais com menor presença de empresas maiores.",

    ("% MEI", "% Pequenas empresas"): "Correlação de -0,12: associação fraca. Onde há mais MEIs, há levemente menos pequenas empresas proporcionalmente.",

    ("% MEI", "% Demais empresas"): "Correlação de -0,19: associação fraca. Municípios com mais MEIs tendem a ter proporcionalmente menos empresas de médio e grande porte.",

    ("IPDM total", "Escolaridade"): "Correlação de 0,76: associação forte. Escolaridade é um dos pilares do IPDM — municípios com população mais educada tendem a apresentar melhores condições de vida em geral.",

    ("IPDM total", "Longevidade"): "Correlação de 0,65: associação forte. Longevidade também compõe o IPDM — municípios com habitantes que vivem mais tendem a ter maior desenvolvimento.",

    ("IPDM total", "Riqueza"): "Correlação de 0,54: associação moderada. Riqueza contribui para o desenvolvimento, mas educação e longevidade têm associação ainda mais forte — renda elevada, por si só, não garante desenvolvimento.",

    ("IPDM total", "População"): "Correlação de 0,03: sem associação. Ser grande ou pequeno não determina o desenvolvimento — há municípios pequenos muito desenvolvidos e grandes com indicadores baixos.",

    ("IPDM total", "Total de empresas"): "Correlação de 0,03: sem associação. Ter muitas empresas não está relacionado a maior desenvolvimento — o tipo de negócio parece importar mais do que o volume.",

    ("IPDM total", "Densidade empresarial"): "Correlação de 0,11: associação muito fraca. Mais empresas por habitante tem leve relação com desenvolvimento, mas não é fator determinante.",

    ("IPDM total", "% Microempresas"): "Correlação de -0,17: associação fraca negativa. Municípios com mais microempresas tendem a ter levemente menor desenvolvimento.",

    ("IPDM total", "% Pequenas empresas"): "Correlação de 0,23: associação fraca-moderada. Pequenas empresas têm leve associação positiva com desenvolvimento — geram mais empregos formais do que MEIs e microempresas.",

    ("IPDM total", "% Demais empresas"): "Correlação de 0,10: associação fraca. Empresas maiores têm leve associação positiva com desenvolvimento, mas são raras nos municípios menores.",

    ("Escolaridade", "Longevidade"): "Correlação de 0,25: associação moderada. Municípios com população mais escolarizada tendem a ter melhor expectativa de vida.",

    ("Escolaridade", "Riqueza"): "Correlação de 0,13: associação fraca. Escolaridade e riqueza caminham juntas, mas menos do que se esperaria — municípios ricos com base no agronegócio nem sempre têm alta escolaridade.",

    ("Escolaridade", "População"): "Correlação de -0,04: sem associação. O tamanho do município não está relacionado ao nível de escolaridade.",

    ("Escolaridade", "Total de empresas"): "Correlação de -0,04: sem associação. Volume de empresas não reflete o nível educacional do município.",

    ("Escolaridade", "Densidade empresarial"): "Correlação de 0,00: sem associação.",

    ("Escolaridade", "% Microempresas"): "Correlação de -0,01: sem associação relevante.",

    ("Escolaridade", "% Pequenas empresas"): "Correlação de 0,06: sem associação relevante.",

    ("Escolaridade", "% Demais empresas"): "Correlação de -0,02: sem associação relevante.",

    ("Longevidade", "Riqueza"): "Correlação de 0,04: associação muito fraca. Riqueza tem pouca relação com longevidade — acesso a saúde pública e saneamento parecem ser mais determinantes.",

    ("Longevidade", "População"): "Correlação de 0,01: sem associação. Municípios grandes e pequenos têm expectativas de vida similares.",

    ("Longevidade", "Total de empresas"): "Correlação de 0,01: sem associação.",

    ("Longevidade", "Densidade empresarial"): "Correlação de -0,08: sem associação relevante.",

    ("Longevidade", "% Microempresas"): "Correlação de -0,03: sem associação relevante.",

    ("Longevidade", "% Pequenas empresas"): "Correlação de 0,07: sem associação relevante.",

    ("Longevidade", "% Demais empresas"): "Correlação de -0,00: sem associação relevante.",

    ("Riqueza", "População"): "Correlação de 0,12: associação fraca. Municípios mais populosos tendem a gerar um pouco mais de riqueza per capita, mas a relação não é expressiva.",

    ("Riqueza", "Total de empresas"): "Correlação de 0,10: associação fraca. Mais empresas tem leve associação com maior riqueza, mas o tipo de negócio parece importar mais.",

    ("Riqueza", "Densidade empresarial"): "Correlação de 0,33: associação moderada. Municípios com mais empresas por habitante tendem a ser mais ricos — uma economia local mais ativa favorece a geração de renda.",

    ("Riqueza", "% Microempresas"): "Correlação de -0,33: associação moderada negativa. Onde microempresas dominam, a riqueza per capita tende a ser menor.",

    ("Riqueza", "% Pequenas empresas"): "Correlação de 0,36: associação moderada. Pequenas empresas têm associação positiva com riqueza local — maior faturamento e mais empregos formais do que MEIs e microempresas.",

    ("Riqueza", "% Demais empresas"): "Correlação de 0,24: associação fraca-moderada. Empresas maiores têm associação positiva com a riqueza municipal.",

    ("População", "Total de empresas"): "Correlação de 1,00: associação perfeita — municípios maiores têm mais empresas no total. Reflete apenas escala, não qualidade ou estrutura econômica.",

    ("População", "Densidade empresarial"): "Correlação de 0,18: associação fraca. Ser mais populoso não garante mais empresas por habitante.",

    ("População", "% Microempresas"): "Correlação de -0,24: municípios mais populosos tendem a ter levemente menos microempresas proporcionalmente.",

    ("População", "% Pequenas empresas"): "Correlação de 0,24: municípios maiores tendem a ter levemente mais pequenas empresas proporcionalmente.",

    ("População", "% Demais empresas"): "Correlação de 0,19: municípios mais populosos concentram levemente mais empresas de médio e grande porte.",

    ("Total de empresas", "Densidade empresarial"): "Correlação de 0,17: ter mais empresas no total não garante maior densidade — municípios grandes têm mais empresas mas também mais habitantes.",

    ("Total de empresas", "% Microempresas"): "Correlação de -0,22: municípios com mais empresas no total tendem a ter levemente menos microempresas proporcionalmente.",

    ("Total de empresas", "% Pequenas empresas"): "Correlação de 0,22: municípios com mais empresas tendem a ter levemente mais pequenas empresas proporcionalmente.",

    ("Total de empresas", "% Demais empresas"): "Correlação de 0,18: municípios com mais empresas concentram levemente mais negócios de médio e grande porte.",

    ("Densidade empresarial", "% Microempresas"): "Correlação de -0,26: municípios com mais empresas por habitante tendem a ter menos microempresas proporcionalmente — economias mais densas tendem a ser mais diversificadas.",

    ("Densidade empresarial", "% Pequenas empresas"): "Correlação de 0,16: maior densidade empresarial tem leve associação com mais pequenas empresas.",

    ("Densidade empresarial", "% Demais empresas"): "Correlação de 0,26: municípios com maior densidade empresarial tendem a ter mais empresas de médio e grande porte proporcionalmente.",

    ("% Microempresas", "% Pequenas empresas"): "Correlação de -0,72: associação negativa forte. Onde microempresas dominam, pequenas empresas têm menor participação — e vice-versa. As categorias tendem a se excluir na composição local.",

    ("% Microempresas", "% Demais empresas"): "Correlação de -0,93: associação negativa muito forte. Municípios com muitas microempresas têm muito poucas empresas maiores — as categorias praticamente se excluem.",

    ("% Pequenas empresas", "% Demais empresas"): "Correlação de 0,43: associação moderada positiva. Municípios com mais pequenas empresas tendem a ter também mais empresas de médio e grande porte — sinal de ecossistema empresarial mais diversificado.",
}

def buscar_interpretacao(label_x, label_y):
    chave = (label_x, label_y)
    chave_inv = (label_y, label_x)
    return interpretacoes.get(chave) or interpretacoes.get(chave_inv) or "Sem interpretação disponível para esta combinação."

def montar_scatter(df_scatter, label_x, label_y):
    col_x = variaveis_scatter[label_x]
    col_y = variaveis_scatter[label_y]

    df_plot = df_scatter[["municipio", "grupo_ipdm", col_x, col_y]].dropna()

    x = df_plot[col_x]
    y = df_plot[col_y]
    coef = np.polyfit(x, y, 1)
    linha = np.poly1d(coef)
    x_linha = np.linspace(x.min(), x.max(), 100)
    y_linha = linha(x_linha)

    correlacao = x.corr(y)
    correlacao_txt = f"{correlacao:.2f}".replace(".", ",")


    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_plot[col_x].tolist(),
        y=df_plot[col_y].tolist(),
        mode="markers",
        marker=dict(size=5, color="rgba(0, 200, 150, 0.6)", opacity=0.8),
        name="Municípios",
        customdata=df_plot[["municipio", "grupo_ipdm"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            f"{label_x}: " + "%{x:.2f}<br>"
            f"{label_y}: " + "%{y:.2f}<br>"
            "Classificação IPDM: %{customdata[1]}"
            "<extra></extra>"
        )
    ))

    fig.add_trace(go.Scatter(
        x=x_linha.tolist(),
        y=y_linha.tolist(),
        mode="lines",
        line=dict(width=3, color="rgba(255, 99, 132, 1)"),
        name="Tendência"
    ))

    fig.update_layout(
        title=f"{label_x} vs {label_y}",
        xaxis_title=label_x,
        yaxis_title=label_y,
        template="plotly_dark",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig, correlacao_txt


# =========================
# FUNÇÃO DO MAPA
# =========================

def criar_mapa(geo_final, variavel_label, variavel):
    variaveis_log = {"populacao", "total_empresas"}

    if variavel == "grupo_ipdm":
        gdf = geo_final.copy()
    else:
        gdf = geo_final.dropna(subset=[variavel]).copy()

    gdf = gdf.reset_index(drop=True)

    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": row["code_muni"],
                "geometry": row["geometry"].__geo_interface__,
                "properties": {"code_muni": row["code_muni"]}
            }
            for _, row in gdf.iterrows()
        ]
    }

    colunas_custom = [
        "grupo_ipdm", "ipdm_total", "escolaridade", "longevidade", "riqueza",
        "populacao", "total_empresas", "empresas_por_1000_hab",
        "pct_micro", "pct_pequena", "pct_demais", "pct_mei"
    ]
    customdata = gdf[colunas_custom].values

    hover_base = (
        "━━━ IPDM ━━━<br>"
        "Classificação: %{customdata[0]}<br>"
        "IPDM total: %{customdata[1]:.3f}<br>"
        "Escolaridade: %{customdata[2]:.3f}<br>"
        "Longevidade: %{customdata[3]:.3f}<br>"
        "Riqueza: %{customdata[4]:.3f}<br>"
        "<br>"
        "━━━ Empresas ━━━<br>"
        "População: %{customdata[5]:,.0f}<br>"
        "Total de empresas: %{customdata[6]:,.0f}<br>"
        "Densidade (emp/1000 hab): %{customdata[7]:.1f}<br>"
        "% Microempresas: %{customdata[8]:.1f}%<br>"
        "% Pequenas: %{customdata[9]:.1f}%<br>"
        "% Demais: %{customdata[10]:.1f}%<br>"
        "% MEI: %{customdata[11]:.1f}%<br>"
        "<extra></extra>"
    )

    formatos = {
        "grupo_ipdm":            "<b>%{text}</b><br>Classificação IPDM: %{customdata[0]}<br><br>",
        "ipdm_total":            "<b>%{text}</b><br>IPDM total: %{customdata[1]:.3f}<br><br>",
        "escolaridade":          "<b>%{text}</b><br>Escolaridade: %{customdata[2]:.3f}<br><br>",
        "longevidade":           "<b>%{text}</b><br>Longevidade: %{customdata[3]:.3f}<br><br>",
        "riqueza":               "<b>%{text}</b><br>Riqueza: %{customdata[4]:.3f}<br><br>",
        "populacao":             "<b>%{text}</b><br>População: %{customdata[5]:,.0f}<br><br>",
        "total_empresas":        "<b>%{text}</b><br>Total de empresas: %{customdata[6]:,.0f}<br><br>",
        "empresas_por_1000_hab": "<b>%{text}</b><br>Densidade: %{customdata[7]:.1f}<br><br>",
        "pct_micro":             "<b>%{text}</b><br>% Microempresas: %{customdata[8]:.1f}%<br><br>",
        "pct_pequena":           "<b>%{text}</b><br>% Pequenas: %{customdata[9]:.1f}%<br><br>",
        "pct_demais":            "<b>%{text}</b><br>% Demais: %{customdata[10]:.1f}%<br><br>",
        "pct_mei":               "<b>%{text}</b><br>% MEI: %{customdata[11]:.1f}%<br><br>",
    }

    hovertemplate = formatos.get(variavel, "<b>%{text}</b><br><br>") + hover_base

    fig_mapa = go.Figure()

    if variavel == "grupo_ipdm":
        ordem = ["Baixa", "Média", "Alta", "Muito alta"]
        gdf["_cor_idx"] = gdf["grupo_ipdm"].apply(lambda x: ordem.index(x))

        fig_mapa.add_trace(go.Choroplethmapbox(
            geojson=geojson,
            locations=gdf["code_muni"].tolist(),
            z=gdf["_cor_idx"].tolist(),
            colorscale=[
                [0.00, "#D7191C"],
                [0.33, "#F4A6B7"],
                [0.66, "#74ADD1"],
                [1.00, "#08306B"],
            ],
            zmin=0, zmax=3,
            marker_opacity=0.8,
            marker_line_width=0.5,
            colorbar=dict(
                tickvals=[0, 1, 2, 3],
                ticktext=["Baixa", "Média", "Alta", "Muito alta"],
                title="IPDM",
            ),
            text=gdf["municipio"].tolist(),
            customdata=customdata,
            hovertemplate=hovertemplate,
        ))

    elif variavel in variaveis_log:
        gdf["_z"] = np.log10(gdf[variavel].clip(lower=1))
        ticks_possiveis = [100, 1_000, 5_000, 10_000, 50_000,
                           100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
        z_min = gdf["_z"].min()
        z_max = gdf["_z"].max()
        ticks_filtrados = [t for t in ticks_possiveis
                           if np.log10(t) >= z_min and np.log10(t) <= z_max]

        fig_mapa.add_trace(go.Choroplethmapbox(
            geojson=geojson,
            locations=gdf["code_muni"].tolist(),
            z=gdf["_z"].tolist(),
            zmin=z_min, zmax=z_max,
            colorscale="YlOrRd",
            marker_opacity=0.8,
            marker_line_width=0.5,
            colorbar=dict(
                title=variavel_label,
                tickvals=[np.log10(t) for t in ticks_filtrados],
                ticktext=[f"{t:,.0f}".replace(",", ".") for t in ticks_filtrados],
            ),
            text=gdf["municipio"].tolist(),
            customdata=customdata,
            hovertemplate=hovertemplate,
        ))

    else:
        fig_mapa.add_trace(go.Choroplethmapbox(
            geojson=geojson,
            locations=gdf["code_muni"].tolist(),
            z=gdf[variavel].tolist(),
            colorscale="YlOrRd",
            marker_opacity=0.8,
            marker_line_width=0.5,
            colorbar=dict(title=variavel_label),
            text=gdf["municipio"].tolist(),
            customdata=customdata,
            hovertemplate=hovertemplate,
        ))

    fig_mapa.update_layout(
        title=f"{variavel_label} por município de São Paulo",
        mapbox=dict(
            style="carto-positron",
            center={"lat": -22.3, "lon": -48.5},
            zoom=5.2,
        ),
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        height=450,
    )


    return fig_mapa

# =========================
# MAPA + SCATTER LADO A LADO
# =========================


col_mapa, col_scatter = st.columns(2)

with col_mapa:
    opcoes_mapa = {
        "Classificação IPDM": "grupo_ipdm",
        "IPDM total": "ipdm_total",
        "Riqueza": "riqueza",
        "Escolaridade": "escolaridade",
        "Longevidade": "longevidade",
        "População": "populacao",
        "Total de empresas": "total_empresas",
        "Densidade empresarial": "empresas_por_1000_hab",
        "% microempresas": "pct_micro",
        "% pequenas empresas": "pct_pequena",
        "% demais empresas": "pct_demais",
        "% MEI": "pct_mei",
    }
    with st.container(border=True):

        st.subheader("Distribuição territorial")

        variavel_label = st.selectbox(
            "Explorar por...",
            list(opcoes_mapa.keys()),
            key="selectbox_mapa"
        )
        variavel = opcoes_mapa[variavel_label]

        st.caption(f"O mapa mostra a distribuição dos municípios paulistas por **{variavel_label.lower()}**. Passe o mouse sobre um município para ver todos os indicadores.")

        fig_mapa = criar_mapa(
            geo_final=geo_final,
            variavel_label=variavel_label,
            variavel=variavel
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

with col_scatter:
    with st.container(border=True):
        st.subheader("Relação entre variáveis")
        st.caption("Selecione duas variáveis para explorar como elas se relacionam nos municípios paulistas. A linha vermelha indica a tendência geral.")

        col_x_sel, col_y_sel = st.columns(2)

        with col_x_sel:
            label_x = st.selectbox(
                "Eixo X",
                list(variaveis_scatter.keys()),
                index=0,
                key="scatter_x"
            )

        with col_y_sel:
            label_y = st.selectbox(
                "Eixo Y",
                list(variaveis_scatter.keys()),
                index=1,
                key="scatter_y"
            )

        if label_x == label_y:
            st.warning("Escolha variáveis diferentes para os eixos X e Y.")
        else:
            fig_scatter, correlacao_txt = montar_scatter(df_scatter, label_x, label_y)
            st.plotly_chart(fig_scatter, use_container_width=True)

            
            st.write(buscar_interpretacao(label_x, label_y))
        
                    

with st.sidebar:
    st.image("https://s4.static.brasilescola.uol.com.br/be/2021/05/bandeira-sp.jpg", width=60)
    st.title("Estrutura Empresarial e Desenvolvimento Municipal de SP")

    st.divider()

    st.markdown("### 📌 Sobre o dashboard")
    st.markdown("""
    Este dashboard investiga se **a quantidade e o tipo de empresas** de um município
    estão relacionados ao seu **nível de desenvolvimento socioeconômico**, medido pelo IPDM.

    A hipótese central é que **mais empresas não significam, necessariamente, mais desenvolvimento** —
    e que a estrutura econômica importa mais do que o volume.
    """)

    st.divider()

    st.markdown("### 🧭 Como usar")
    st.markdown("""
    - **Cards no topo:** visão geral do estado de SP
    - **Mapa:** explore a distribuição geográfica de qualquer variável
    - **Gráfico de dispersão:** investigue a relação entre duas variáveis
    - **Passe o mouse** sobre qualquer município no mapa para ver todos os indicadores
    """)

    st.divider()

    st.markdown("### 📈 O que é o IPDM?")
    st.markdown("""
    O **Índice Paulista de Desenvolvimento Municipal (IPDM)** é um indicador criado pela
    Fundação SEADE para medir o desenvolvimento dos 645 municípios paulistas —
    funcionando de forma similar ao IDH, mas com foco no estado de São Paulo
    e uso pela gestão pública estadual.

    Varia de **0 a 1** e é composto pela média de três dimensões:
    - **Riqueza:** PIB per capita, renda dos trabalhadores formais e consumo de energia elétrica
    - **Longevidade:** taxas de mortalidade infantil, perinatal e de adultos
    - **Escolaridade:** acesso à creche, proficiência em português e matemática e distorção idade-série

    Os municípios são classificados em quatro grupos:
    **Muito Alta** (> 0,600) · **Alta** (0,550–0,600) · **Média** (0,500–0,550) · **Baixa** (≤ 0,500)
    """)

    st.divider()

    st.markdown("### 📁 Fontes")
    st.markdown("""
    - **Empresas:** Fundação SEADE — Painel de Empresas (2026)
    [repositorio.seade.gov.br](https://repositorio.seade.gov.br/dataset/seade-empresa)

    - **IPDM:** Fundação SEADE — Índice Paulista de Desenvolvimento Municipal (2025)
    [dadosabertos.sp.gov.br](https://dadosabertos.sp.gov.br/dataset/indice-paulista-de-desenvolvimento-municipal-ipdm)

    - **População:** IBGE — Censo Demográfico (2022)
    [repositorio.seade.gov.br](https://repositorio.seade.gov.br/dataset/seade-censo-2022)
    """)

    st.divider()

    st.markdown("### ⚠️ Limitações")
    st.markdown("""
    - **Correlação não é causalidade** — as relações observadas indicam associações,
    não relações de causa e efeito
    - Os dados representam um **recorte temporal** específico e podem não refletir
    mudanças recentes
    - Algumas variáveis do IPDM utilizam **estimativas e projeções** sujeitas a revisão
    """)

    st.divider()

    st.markdown("### 👨‍💻 Desenvolvido por")
    st.markdown("""
    **Ricardo Fernando dos Santos**
                
    São Paulo, Brasil

    [![GitHub](https://img.shields.io/badge/GitHub-st--ricardof-181717?logo=github)](https://github.com/st-ricardof)
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-st--ricardof-0A66C2?logo=linkedin)](https://www.linkedin.com/in/st-ricardof/)
    [![Email](https://img.shields.io/badge/Email-st.ricardof@gmail.com-D14836?logo=gmail)](mailto:st.ricardof@gmail.com)
    """)