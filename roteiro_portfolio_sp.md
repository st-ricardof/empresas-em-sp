# Roteiro de Portfólio — Projeto SP
## "Crescimento para quem? Estrutura empresarial e distribuição de riqueza nos municípios de São Paulo"

**Autor:** Ricardo Fernando dos Santos
**Prazo estimado:** 10–12 dias
**Nível entregue:** Sênior / Produto
**Stack:** Python · DuckDB · Plotly · Streamlit · API CNPJ · API Claude (IA)
**Deploy:** Streamlit Community Cloud (gratuito)

---

## Visão geral do que você vai construir

Um **app web interativo** — não um notebook estático — onde qualquer pessoa pode:

1. Explorar os 645 municípios de SP em dashboards com gráficos interativos
2. Ver a tipologia de cada município (4 perfis econômicos)
3. **Digitar um CNPJ** → o app identifica o município da empresa → mostra onde ela está na tipologia → uma IA gera um parágrafo de análise contextual

O resultado é um projeto que parece **produto**, não exercício acadêmico.

---

## Por que essa stack?

| Tecnologia | Por que usar | Alternativa anterior |
|---|---|---|
| **DuckDB** | Banco de dados analítico embutido em Python. Você faz SQL direto nos CSVs, sem precisar instalar nada. Mostra que você trabalha com dados como no mundo real | pandas puro |
| **Plotly** | Gráficos interativos (hover, zoom, filtros). O usuário interage com os dados | matplotlib estático |
| **Streamlit** | Transforma scripts Python em app web com poucas linhas. Deploy gratuito | Jupyter notebook |
| **API CNPJ** | Gratuita, sem cadastro. Retorna município, razão social, setor da empresa | — |
| **API Claude** | Gera análise em linguagem natural a partir dos dados do município | — |

---

## Estrutura de pastas

```
sp-crescimento-para-quem/
│
├── README.md                  ← Vitrine do projeto no GitHub
├── requirements.txt           ← Dependências
├── .gitignore                 ← Ignora data/raw/ e .env
├── .env                       ← Sua chave da API Claude (NUNCA comitar)
│
├── data/
│   ├── raw/                   ← Arquivos baixados (não commitados)
│   └── processed/
│       └── dataset_base.csv   ← Dataset limpo e unificado
│
├── notebooks/
│   ├── 01_exploracao.ipynb
│   ├── 02_limpeza_e_merge.ipynb
│   └── 03_analises.ipynb      ← Onde você valida as análises antes de colocar no app
│
├── app/
│   ├── main.py                ← Ponto de entrada do Streamlit
│   ├── pages/
│   │   ├── 01_visao_geral.py
│   │   ├── 02_tipologia.py
│   │   └── 03_busca_cnpj.py
│   └── utils/
│       ├── data_loader.py     ← Carrega e cacheia os dados
│       ├── queries.py         ← Todas as queries DuckDB
│       ├── charts.py          ← Todos os gráficos Plotly
│       └── ai_analysis.py     ← Chamada para API Claude
│
└── outputs/
    └── figures/               ← Prints dos gráficos para o README
```

---

## requirements.txt

```
pandas==2.2.0
numpy==1.26.0
duckdb==0.10.0
plotly==5.18.0
streamlit==1.31.0
requests==2.31.0
anthropic==0.18.0
python-dotenv==1.0.0
openpyxl==3.1.2
```

> **Por que `anthropic` e não `openai`?** O SDK da Anthropic é mais simples
> para começar. O Claude é o modelo que você está usando agora — faz sentido
> demonstrar integração com ele no portfólio.

---

## .gitignore

```gitignore
data/raw/
.env
__pycache__/
*.pyc
.DS_Store
```

---

# ROTEIRO DIA A DIA

---

## DIA 1 — Ambiente e download dos dados

### 1.1 — Configurar o ambiente Python

```bash
# Crie um ambiente virtual (boas práticas — isola as dependências do projeto)
python -m venv venv

# Ative o ambiente
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

> **O que é um ambiente virtual?** É uma pasta isolada com Python e
> bibliotecas só para este projeto. Evita conflitos entre projetos diferentes.
> Boa prática que recrutadores técnicos notam.

### 1.2 — Baixar os dados

Acesse as três URLs e baixe os arquivos para `data/raw/`:

**Dataset 1 — Empresas:**
https://repositorio.seade.gov.br/dataset/seade-empresa

**Dataset 2 — PIB Municipal:**
https://repositorio.seade.gov.br/dataset/pib-municipal-2002-2020

**Dataset 3 — IPRS (Índice Paulista de Responsabilidade Social):**
No repositório SEADE, busque por "IPRS". É um índice que combina renda,
escolaridade e longevidade — mais rico que o IDH para municípios paulistas.

### 1.3 — Primeira exploração (notebook 01)

```python
# notebooks/01_exploracao.ipynb
import pandas as pd
import numpy as np

# --- Empresas ---
emp = pd.read_csv('data/raw/empresas_sp.csv', sep=';', encoding='latin-1')
print("=== SHAPE:", emp.shape)
print("=== COLUNAS:", emp.columns.tolist())
print("=== TIPOS:\n", emp.dtypes)
print("=== NULOS:\n", emp.isnull().sum())
print(emp.head(3))

# --- PIB ---
pib = pd.read_excel('data/raw/pib_municipal.xlsx')
print("\n=== PIB SHAPE:", pib.shape)
print("=== COLUNAS:", pib.columns.tolist())
print(pib.head(3))
```

**Perguntas para responder antes de avançar:**
- Qual coluna identifica o município? Nome ou código IBGE?
- O código IBGE tem 6 ou 7 dígitos? (O padrão nacional é 7)
- Qual o ano de referência de cada base?
- Como o porte das empresas está categorizado? (MEI, micro, pequena, média, grande)
- O PIB per capita já vem calculado ou precisa dividir pelo número de habitantes?

> **Por que o código IBGE importa tanto?** Municípios têm nomes com variações
> ("São Paulo", "S. Paulo", "SAO PAULO"). O código numérico é único e imutável.
> Sempre junte bases por código, nunca por nome.

---

## DIA 2 — Limpeza e construção do dataset base

### 2.1 — Padronizar o código do município

```python
# notebooks/02_limpeza_e_merge.ipynb
import pandas as pd
import numpy as np

emp = pd.read_csv('data/raw/empresas_sp.csv', sep=';', encoding='latin-1')
pib = pd.read_excel('data/raw/pib_municipal.xlsx')

# Verifique como o código aparece em cada base
print(emp['cod_municipio'].dtype)      # deve ser int64 ou object
print(emp['cod_municipio'].head())

print(pib['cod_municipio'].dtype)
print(pib['cod_municipio'].head())

# Se um deles tiver como string com zeros à esquerda:
emp['cod_municipio'] = emp['cod_municipio'].astype(str).str.zfill(7)
pib['cod_municipio'] = pib['cod_municipio'].astype(str).str.zfill(7)

# Se vier como inteiro de 6 dígitos (sem o dígito verificador):
# Ambas as bases precisam estar no mesmo padrão
```

### 2.2 — Agregar empresas por município

```python
# Agrupa tudo por município — soma as quantidades por porte
# ATENÇÃO: ajuste os nomes das colunas conforme o que você encontrou no dia 1

emp_mun = emp.groupby('cod_municipio').agg(
    total_empresas = ('qtd_empresas', 'sum'),
    total_meis     = ('qtd_mei', 'sum'),
    total_micro    = ('qtd_micro', 'sum'),
    total_peq      = ('qtd_pequena', 'sum'),
    total_med      = ('qtd_media', 'sum'),
    total_grandes  = ('qtd_grande', 'sum'),
).reset_index()

# Calcular proporções — dividir pela quantidade total e multiplicar por 100
# Proporções são mais comparáveis que números absolutos (um município grande
# sempre vai ter mais empresas que um pequeno)
emp_mun['pct_mei']     = emp_mun['total_meis']    / emp_mun['total_empresas'] * 100
emp_mun['pct_grandes'] = emp_mun['total_grandes'] / emp_mun['total_empresas'] * 100
emp_mun['pct_micro']   = emp_mun['total_micro']   / emp_mun['total_empresas'] * 100

print(f"Municípios no dataset de empresas: {len(emp_mun)}")
print(emp_mun.describe())
```

### 2.3 — Limpar o PIB

```python
# Seleciona apenas o ano mais recente disponível (provavelmente 2020)
pib_2020 = pib[pib['ano'] == 2020].copy()  # ajuste o nome da coluna de ano

# Colunas que interessam
pib_limpo = pib_2020[[
    'cod_municipio', 'nome_municipio',
    'pib_total', 'pib_per_capita',
    'vab_agropecuaria', 'vab_industria', 'vab_servicos', 'vab_adm_publica'
]].copy()

# Distribuição setorial em percentual
total_vab = (pib_limpo['vab_agropecuaria'] + pib_limpo['vab_industria'] +
             pib_limpo['vab_servicos']     + pib_limpo['vab_adm_publica'])

pib_limpo['pct_agropecuaria'] = pib_limpo['vab_agropecuaria'] / total_vab * 100
pib_limpo['pct_industria']    = pib_limpo['vab_industria']    / total_vab * 100
pib_limpo['pct_servicos']     = pib_limpo['vab_servicos']     / total_vab * 100
pib_limpo['pct_adm_publica']  = pib_limpo['vab_adm_publica']  / total_vab * 100

print(f"Municípios no PIB: {len(pib_limpo)}")
```

### 2.4 — Merge e enriquecimento

```python
# Junta as duas bases pela chave comum (código do município)
# how='inner' mantém só os municípios presentes nas DUAS bases
df = pib_limpo.merge(emp_mun, on='cod_municipio', how='inner')
print(f"Municípios após merge: {len(df)}")
# Se perder muitos municípios, revise o código — problema de formato da chave

# --- Variáveis derivadas ---

# Índice de informalidade: quanto maior, mais a estrutura é de subsistência
df['indice_informalidade'] = df['total_meis'] / df['total_empresas']

# Índice de diversificação econômica (baseado no HHI invertido)
# HHI = soma dos quadrados das participações de cada setor
# Quanto mais concentrado em um setor, mais próximo de 1 o HHI
# Invertemos: 0 = concentrado, 1 = diversificado
def calcular_diversificacao(row):
    setores = [
        row['pct_agropecuaria'] / 100,
        row['pct_industria']    / 100,
        row['pct_servicos']     / 100,
        row['pct_adm_publica']  / 100,
    ]
    setores = [s for s in setores if s > 0]
    if not setores:
        return np.nan
    hhi = sum(s**2 for s in setores)
    return round(1 - hhi, 4)

df['indice_diversificacao'] = df.apply(calcular_diversificacao, axis=1)

# Tipologia: classifica cada município em um dos 4 perfis
mediana_pib       = df['pib_per_capita'].median()
mediana_pct_grandes = df['pct_grandes'].median()

def classificar_municipio(row):
    pib_alto           = row['pib_per_capita'] > mediana_pib
    estrutura_sofist   = row['pct_grandes']    > mediana_pct_grandes

    if pib_alto and estrutura_sofist:
        return 'Dinâmico Consolidado'
    elif pib_alto and not estrutura_sofist:
        return 'Rico Concentrado'
    elif not pib_alto and estrutura_sofist:
        return 'Estruturado em Desenvolvimento'
    else:
        return 'Frágil'

df['tipologia'] = df.apply(classificar_municipio, axis=1)

# Salvar
df.to_csv('data/processed/dataset_base.csv', index=False)
print(df['tipologia'].value_counts())
print(df.describe())
```

> **Por que criar as variáveis derivadas aqui e não no app?**
> O princípio do pipeline de dados: transformações acontecem uma vez,
> no processamento, não toda vez que o usuário carrega a página.
> O app apenas lê o dado já pronto.

---

## DIA 3 — Análise exploratória e validação

### 3.1 — Instalar e entender o DuckDB

```python
# notebooks/03_analises.ipynb
import duckdb

# DuckDB lê o CSV diretamente — sem precisar carregar no pandas antes
conn = duckdb.connect()

# Registre o arquivo como uma tabela virtual
conn.execute("CREATE VIEW municipios AS SELECT * FROM 'data/processed/dataset_base.csv'")

# Agora você faz SQL normal
resultado = conn.execute("""
    SELECT
        nome_municipio,
        pib_per_capita,
        pct_mei,
        tipologia
    FROM municipios
    WHERE pib_per_capita > 50000
    ORDER BY pib_per_capita DESC
    LIMIT 10
""").df()  # .df() converte o resultado para pandas DataFrame

print(resultado)
```

> **Por que DuckDB?** No mundo real, você não carrega CSVs no pandas —
> você faz queries em bancos de dados. DuckDB simula esse ambiente localmente,
> suporta SQL completo, e é muito mais rápido que pandas para agregações.
> Aparece no portfólio como diferencial de maturidade técnica.

### 3.2 — Análises de validação (antes de colocar no app)

```python
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

# Carrega com pandas para facilitar os cálculos estatísticos
df = conn.execute("SELECT * FROM municipios").df()

# --- Validação 1: a correlação central ---
corr, pval = stats.pearsonr(df['total_empresas'], df['pib_per_capita'])
print(f"Correlação empresas × PIB per capita: {corr:.3f} (p={pval:.4f})")
# Interprete: se r < 0.3, correlação fraca. Isso é o achado.

# --- Validação 2: distribuição da tipologia ---
print(df['tipologia'].value_counts())
print(df.groupby('tipologia')['pib_per_capita'].describe())

# --- Validação 3: paradoxo das MEIs ---
corr_mei, _ = stats.pearsonr(df['pct_mei'], df['pib_per_capita'])
print(f"Correlação % MEI × PIB per capita: {corr_mei:.3f}")
# Espera-se negativa: mais MEI = menos PIB per capita

# --- Scatter interativo para exploração ---
fig = px.scatter(
    df,
    x='pct_mei',
    y='pib_per_capita',
    color='tipologia',
    hover_name='nome_municipio',      # ao passar o mouse, mostra o nome
    hover_data=['total_empresas', 'pct_grandes'],
    title='% de MEIs × PIB per capita',
    labels={
        'pct_mei': '% de MEIs no total de empresas',
        'pib_per_capita': 'PIB per capita (R$)',
    }
)
fig.show()  # abre no browser
```

> **Por que Plotly em vez de matplotlib?**
> Matplotlib gera imagem estática. Plotly gera HTML interativo:
> hover, zoom, pan, filtros por clique na legenda.
> No app Streamlit, o usuário interage diretamente com o gráfico.

---

## DIA 4 — Estrutura do app Streamlit

### 4.1 — Entendendo Streamlit em 10 minutos

Streamlit funciona de cima para baixo: cada vez que o usuário interage
com qualquer elemento, o script roda do início ao fim novamente.
Por isso, usamos `@st.cache_data` para não recarregar os dados toda vez.

```python
# Teste rápido: crie um arquivo teste.py e rode: streamlit run teste.py
import streamlit as st

st.title("Olá, Streamlit!")
st.write("Este é um app web feito em Python.")

numero = st.slider("Escolha um número", 0, 100, 50)
st.write(f"Você escolheu: {numero}")
```

```bash
streamlit run teste.py
# Abre automaticamente em http://localhost:8501
```

### 4.2 — Carregamento e cache dos dados

```python
# app/utils/data_loader.py
import pandas as pd
import duckdb
import streamlit as st

@st.cache_data  # executa UMA vez e cacheia — evita recarregar a cada interação
def carregar_dados():
    """Carrega o dataset base e retorna pandas DataFrame."""
    df = pd.read_csv('data/processed/dataset_base.csv')
    return df

@st.cache_resource  # para conexões de banco — cacheia o objeto de conexão
def get_duckdb_connection():
    """Retorna uma conexão DuckDB com o dataset já registrado."""
    conn = duckdb.connect()
    conn.execute("""
        CREATE OR REPLACE VIEW municipios AS
        SELECT * FROM 'data/processed/dataset_base.csv'
    """)
    return conn
```

> **`@st.cache_data` vs `@st.cache_resource`:** `cache_data` é para dados
> serializáveis (DataFrames, listas, dicionários). `cache_resource` é para
> objetos de conexão que não podem ser copiados. Use um para cada caso.

### 4.3 — Todas as queries em um arquivo só

```python
# app/utils/queries.py
import duckdb

def get_visao_geral(conn):
    return conn.execute("""
        SELECT
            tipologia,
            COUNT(*)                          AS n_municipios,
            ROUND(AVG(pib_per_capita), 0)     AS pib_medio,
            ROUND(AVG(pct_mei), 1)            AS pct_mei_media,
            ROUND(AVG(indice_diversificacao), 3) AS diversificacao_media
        FROM municipios
        GROUP BY tipologia
        ORDER BY pib_medio DESC
    """).df()

def get_scatter_empresas_pib(conn):
    return conn.execute("""
        SELECT
            nome_municipio,
            total_empresas,
            pib_per_capita,
            pct_mei,
            pct_grandes,
            tipologia,
            indice_diversificacao
        FROM municipios
    """).df()

def get_municipio_por_codigo(conn, cod_municipio: str):
    return conn.execute(f"""
        SELECT *
        FROM municipios
        WHERE cod_municipio = '{cod_municipio}'
    """).df()

def get_ranking_pib(conn, n=20):
    return conn.execute(f"""
        SELECT
            nome_municipio,
            pib_per_capita,
            tipologia,
            pct_mei,
            pct_grandes
        FROM municipios
        ORDER BY pib_per_capita DESC
        LIMIT {n}
    """).df()
```

> **Por que centralizar as queries?** Facilita manutenção — se precisar
> mudar uma query, você muda em um lugar só. É também o padrão em engenharia
> de software (separação de responsabilidades).

---

## DIA 5 — Página 1: Visão Geral

```python
# app/pages/01_visao_geral.py
import streamlit as st
import plotly.express as px
from utils.data_loader import carregar_dados, get_duckdb_connection
from utils.queries import get_visao_geral, get_scatter_empresas_pib, get_ranking_pib

st.set_page_config(page_title="Visão Geral — SP", layout="wide")

st.title("Crescimento para quem?")
st.subheader("Estrutura empresarial e distribuição de riqueza nos municípios de SP")

st.markdown("""
São Paulo é o estado mais rico do Brasil. Mas essa riqueza está distribuída como?
Municípios com mais empresas são necessariamente mais ricos?
E quando são mais ricos, essa riqueza chega para a população?
""")

conn = get_duckdb_connection()

# --- Métricas de destaque ---
df = carregar_dados()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Municípios analisados", len(df))
col2.metric("PIB per capita mediano", f"R$ {int(df['pib_per_capita'].median()):,}".replace(',', '.'))
col3.metric("% médio de MEIs", f"{df['pct_mei'].mean():.1f}%")
col4.metric("Municípios frágeis", len(df[df['tipologia'] == 'Frágil']))

st.divider()

# --- Scatter: empresas × PIB ---
st.subheader("Mais empresas = mais riqueza?")
df_scatter = get_scatter_empresas_pib(conn)

fig_scatter = px.scatter(
    df_scatter,
    x='total_empresas',
    y='pib_per_capita',
    color='tipologia',
    hover_name='nome_municipio',
    hover_data={'pct_mei': ':.1f', 'pct_grandes': ':.1f'},
    log_x=True,                   # escala log no X — evita que SP capital esmague tudo
    title='Total de empresas × PIB per capita (escala log)',
    labels={
        'total_empresas': 'Total de empresas (escala log)',
        'pib_per_capita': 'PIB per capita (R$)',
    },
    color_discrete_map={
        'Dinâmico Consolidado':         '#27AE60',
        'Rico Concentrado':              '#F39C12',
        'Estruturado em Desenvolvimento':'#2980B9',
        'Frágil':                        '#E74C3C',
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Insight em destaque
with st.expander("O que este gráfico mostra?"):
    st.markdown("""
    A correlação entre número de empresas e PIB per capita é fraca.
    Municípios com grandes plantas industriais (refinarias, usinas) têm PIB per capita
    altíssimo com poucas empresas — porque a riqueza é do capital instalado, não da
    atividade econômica distribuída.

    Por isso a correlação não é o fim da análise — é o começo da pergunta certa.
    """)

# --- Ranking ---
st.subheader("Ranking de municípios por PIB per capita")
n = st.slider("Quantos municípios mostrar?", 5, 50, 20)
df_rank = get_ranking_pib(conn, n)

fig_rank = px.bar(
    df_rank.sort_values('pib_per_capita'),
    x='pib_per_capita',
    y='nome_municipio',
    color='tipologia',
    orientation='h',
    title=f'Top {n} municípios por PIB per capita',
    labels={'pib_per_capita': 'PIB per capita (R$)', 'nome_municipio': ''},
)
st.plotly_chart(fig_rank, use_container_width=True)
```

---

## DIA 6 — Página 2: Tipologia dos municípios

```python
# app/pages/02_tipologia.py
import streamlit as st
import plotly.express as px
from utils.data_loader import carregar_dados, get_duckdb_connection
from utils.queries import get_visao_geral

st.set_page_config(page_title="Tipologia — SP", layout="wide")
st.title("Os 4 perfis dos municípios paulistas")

st.markdown("""
Classificamos cada município com base em dois eixos:
**riqueza per capita** (eixo Y) e **sofisticação da estrutura empresarial**
(% de grandes empresas, eixo X).

Os quatro quadrantes revelam padrões econômicos distintos — e alguns
contraintuitivos.
""")

conn = get_duckdb_connection()
df = carregar_dados()

# --- Cards explicativos dos 4 tipos ---
col1, col2 = st.columns(2)

with col1:
    st.success("**🟢 Dinâmico Consolidado**")
    st.write("PIB per capita alto + estrutura empresarial sofisticada. "
             "Crescimento distribuído, base produtiva diversificada.")

    st.warning("**🟠 Rico Concentrado**")
    st.write("PIB per capita alto + estrutura empresarial frágil. "
             "Riqueza dependente de poucos empreendimentos de grande porte "
             "(refinarias, usinas, plantas industriais). Não se sustenta no longo prazo.")

with col2:
    st.info("**🔵 Estruturado em Desenvolvimento**")
    st.write("PIB per capita baixo + boa estrutura empresarial. "
             "Base produtiva em construção — potencial de crescimento.")

    st.error("**🔴 Frágil**")
    st.write("PIB per capita baixo + estrutura empresarial informal. "
             "Alta dependência de MEIs e do setor público. Ciclo de vulnerabilidade.")

# --- Scatter de tipologia ---
fig_tipo = px.scatter(
    df,
    x='pct_grandes',
    y='pib_per_capita',
    color='tipologia',
    hover_name='nome_municipio',
    hover_data={
        'pct_mei': ':.1f',
        'indice_diversificacao': ':.3f',
        'tipologia': False
    },
    title='Tipologia: sofisticação empresarial × riqueza per capita',
    labels={
        'pct_grandes': '% de grandes empresas no total',
        'pib_per_capita': 'PIB per capita (R$)',
    },
    color_discrete_map={
        'Dinâmico Consolidado':         '#27AE60',
        'Rico Concentrado':              '#F39C12',
        'Estruturado em Desenvolvimento':'#2980B9',
        'Frágil':                        '#E74C3C',
    }
)

# Linhas de referência (mediana)
mediana_pib     = df['pib_per_capita'].median()
mediana_grandes = df['pct_grandes'].median()

fig_tipo.add_hline(y=mediana_pib,     line_dash='dash', line_color='gray', opacity=0.5)
fig_tipo.add_vline(x=mediana_grandes, line_dash='dash', line_color='gray', opacity=0.5)

st.plotly_chart(fig_tipo, use_container_width=True)

# --- Tabela resumo por tipologia ---
st.subheader("Resumo por tipologia")
df_resumo = get_visao_geral(conn)
st.dataframe(
    df_resumo.rename(columns={
        'tipologia':             'Tipo',
        'n_municipios':          'Municípios',
        'pib_medio':             'PIB per capita médio (R$)',
        'pct_mei_media':         '% MEI médio',
        'diversificacao_media':  'Diversificação média',
    }),
    hide_index=True,
    use_container_width=True,
)
```

---

## DIA 7 — Integração com a API de CNPJ

### 7.1 — Como funciona a API de CNPJ

```python
# Teste no terminal ou num notebook antes de integrar ao app
import requests

cnpj = "60701190000104"   # Itaú — CNPJ sem formatação
url  = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"

resposta = requests.get(url, timeout=10)
dados    = resposta.json()

print(dados['razao_social'])     # Nome da empresa
print(dados['municipio'])        # Cidade
print(dados['uf'])               # Estado
print(dados['cnae_fiscal_descricao'])  # Setor principal
```

> **BrasilAPI** é uma API pública brasileira, gratuita, sem chave, que agrega
> dados da Receita Federal. URL: https://brasilapi.com.br

> **Limitação:** a API retorna o nome do município, não o código IBGE.
> Você vai precisar cruzar pelo nome. Trate variações (maiúsculas, acentos).

### 7.2 — Busca por código IBGE (mais robusto)

```python
# Para cruzar pelo código IBGE, use a API do IBGE para converter nome → código
def get_codigo_ibge(nome_municipio: str, uf: str = "SP") -> str | None:
    """Busca o código IBGE de um município pelo nome e UF."""
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
    resp = requests.get(url, timeout=10)
    municipios = resp.json()

    # Normaliza: remove acentos, coloca em maiúsculas para comparação segura
    import unicodedata
    def normalizar(texto):
        texto = texto.upper()
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )

    nome_norm = normalizar(nome_municipio)
    for m in municipios:
        if normalizar(m['nome']) == nome_norm:
            return str(m['id'])  # código IBGE de 7 dígitos
    return None
```

---

## DIA 8 — Integração com a API Claude (IA)

### 8.1 — Configurar a chave da API

```bash
# Crie sua conta em: https://console.anthropic.com
# Gere uma chave em: Settings → API Keys
# Coloque no arquivo .env (NUNCA no código):
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

```python
# Como carregar a chave no código
from dotenv import load_dotenv
import os

load_dotenv()  # lê o arquivo .env
chave = os.getenv("ANTHROPIC_API_KEY")
```

### 8.2 — Função de análise com IA

```python
# app/utils/ai_analysis.py
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

def gerar_analise_municipio(dados_municipio: dict) -> str:
    """
    Recebe um dicionário com dados do município e retorna
    uma análise em linguagem natural gerada pela IA.
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Monta o prompt com os dados reais do município
    prompt = f"""
Você é um analista de desenvolvimento econômico especializado nos municípios de São Paulo.

Com base nos dados abaixo, escreva um parágrafo analítico (4-6 linhas) sobre o perfil
econômico deste município. Seja preciso, use os números, e explique o que eles significam
para a população e para empresas que consideram operar ali.

DADOS DO MUNICÍPIO:
- Nome: {dados_municipio['nome_municipio']}
- PIB per capita: R$ {dados_municipio['pib_per_capita']:,.0f}
- Tipologia: {dados_municipio['tipologia']}
- % de MEIs no total de empresas: {dados_municipio['pct_mei']:.1f}%
- % de grandes empresas: {dados_municipio['pct_grandes']:.1f}%
- % do PIB em indústria: {dados_municipio['pct_industria']:.1f}%
- % do PIB em serviços: {dados_municipio['pct_servicos']:.1f}%
- % do PIB em administração pública: {dados_municipio['pct_adm_publica']:.1f}%
- Índice de diversificação econômica: {dados_municipio['indice_diversificacao']:.3f} (0=concentrado, 1=diversificado)

Escreva APENAS o parágrafo, sem título, sem tópicos, sem introdução.
"""

    resposta = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return resposta.content[0].text
```

> **Custo:** cada chamada gasta em torno de 300-500 tokens.
> A ~US$3 por milhão de tokens, você vai gastar menos de US$1
> em centenas de consultas. Para um portfólio, o custo é irrelevante.

---

## DIA 9 — Página 3: Busca por CNPJ

```python
# app/pages/03_busca_cnpj.py
import streamlit as st
import requests
import unicodedata
import plotly.express as px
from utils.data_loader import get_duckdb_connection
from utils.queries import get_municipio_por_codigo
from utils.ai_analysis import gerar_analise_municipio

st.set_page_config(page_title="Busca por CNPJ — SP", layout="wide")
st.title("Análise por CNPJ")
st.markdown("""
Digite o CNPJ de uma empresa sediada em São Paulo para ver o perfil econômico
do município onde ela opera — e uma análise gerada por IA.
""")

# --- Input do CNPJ ---
cnpj_raw = st.text_input(
    "CNPJ da empresa",
    placeholder="00.000.000/0001-00",
    max_chars=18
)

# Remove formatação
cnpj = ''.join(filter(str.isdigit, cnpj_raw))

if st.button("Analisar", type="primary") and cnpj:
    if len(cnpj) != 14:
        st.error("CNPJ inválido. Digite 14 dígitos.")
    else:
        with st.spinner("Buscando dados da empresa..."):
            try:
                # 1. Busca dados do CNPJ
                url  = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
                resp = requests.get(url, timeout=10)

                if resp.status_code != 200:
                    st.error("CNPJ não encontrado na base da Receita Federal.")
                    st.stop()

                dados_cnpj = resp.json()

                if dados_cnpj.get('uf') != 'SP':
                    st.warning(f"Esta empresa está em {dados_cnpj.get('uf', '?')}, "
                               "não em São Paulo. A análise cobre apenas municípios paulistas.")
                    st.stop()

                nome_municipio = dados_cnpj['municipio']
                razao_social   = dados_cnpj['razao_social']
                setor          = dados_cnpj.get('cnae_fiscal_descricao', 'Não informado')

                st.success(f"**{razao_social}** — {setor}")

            except Exception as e:
                st.error(f"Erro ao consultar CNPJ: {e}")
                st.stop()

        with st.spinner("Buscando perfil do município..."):
            # 2. Converte nome → código IBGE
            def normalizar(texto):
                texto = texto.upper()
                return ''.join(
                    c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn'
                )

            ibge_resp  = requests.get(
                "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios",
                timeout=10
            ).json()

            cod_municipio = None
            for m in ibge_resp:
                if normalizar(m['nome']) == normalizar(nome_municipio):
                    cod_municipio = str(m['id'])
                    break

            if not cod_municipio:
                st.error(f"Município '{nome_municipio}' não encontrado no dataset.")
                st.stop()

            conn  = get_duckdb_connection()
            df_mun = get_municipio_por_codigo(conn, cod_municipio)

            if df_mun.empty:
                st.error("Município encontrado no IBGE, mas sem dados no dataset do projeto.")
                st.stop()

            mun = df_mun.iloc[0].to_dict()

        # 3. Exibe os dados do município
        st.subheader(f"📍 {mun['nome_municipio']}")

        tipologia_cores = {
            'Dinâmico Consolidado':         'green',
            'Rico Concentrado':              'orange',
            'Estruturado em Desenvolvimento':'blue',
            'Frágil':                        'red',
        }
        cor = tipologia_cores.get(mun['tipologia'], 'gray')
        st.markdown(f"**Tipologia:** :{cor}[{mun['tipologia']}]")

        col1, col2, col3 = st.columns(3)
        col1.metric("PIB per capita", f"R$ {int(mun['pib_per_capita']):,}".replace(',', '.'))
        col2.metric("% de MEIs",       f"{mun['pct_mei']:.1f}%")
        col3.metric("Diversificação",  f"{mun['indice_diversificacao']:.3f}")

        # Gráfico de composição setorial do PIB
        setores = {
            'Indústria':      mun['pct_industria'],
            'Serviços':       mun['pct_servicos'],
            'Agropecuária':   mun['pct_agropecuaria'],
            'Adm. Pública':   mun['pct_adm_publica'],
        }
        fig_pizza = px.pie(
            values=list(setores.values()),
            names=list(setores.keys()),
            title=f"Composição do PIB — {mun['nome_municipio']}",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

        # 4. Análise por IA
        st.subheader("Análise econômica (IA)")
        with st.spinner("Gerando análise..."):
            analise = gerar_analise_municipio(mun)
        st.info(analise)
        st.caption("Análise gerada por Claude (Anthropic) com base nos dados do SEADE/IBGE.")
```

---

## DIA 10 — Ponto de entrada e deploy

### 10.1 — main.py (página inicial)

```python
# app/main.py
import streamlit as st

st.set_page_config(
    page_title="Crescimento para quem? — SP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Crescimento para quem?")
st.subheader("Estrutura empresarial e distribuição de riqueza nos municípios de São Paulo")

st.markdown("""
---
### O que este projeto analisa

São Paulo é o estado mais rico do Brasil. Mas essa riqueza está distribuída como?
Municípios com mais empresas são necessariamente mais ricos?

Este dashboard conecta três bases de dados públicas para responder essas perguntas —
e revela padrões que o senso comum não vê.

---
### Como navegar

Use o menu lateral para acessar as seções:

- **Visão Geral** — Panorama dos 645 municípios, correlações e rankings
- **Tipologia** — Os 4 perfis econômicos dos municípios paulistas
- **Busca por CNPJ** — Digite um CNPJ e veja o perfil do município da empresa, com análise por IA

---
### Fontes de dados
- **Empresas SP:** SEADE/CNPJ
- **PIB Municipal:** SEADE (2020)
- **Municípios:** IBGE
""")
```

### 10.2 — Deploy no Streamlit Community Cloud

```bash
# 1. Certifique que o requirements.txt está atualizado
pip freeze > requirements.txt

# 2. Não commite o .env — use Secrets no Streamlit Cloud
# No painel do Streamlit Cloud: Settings → Secrets
# Cole o conteúdo do .env:
#   ANTHROPIC_API_KEY = "sk-ant-..."

# 3. Commit e push para o GitHub
git add .
git commit -m "feat: app completo com busca por CNPJ e análise por IA"
git push origin main
```

**No Streamlit Community Cloud (share.streamlit.io):**
1. Conecte sua conta GitHub
2. Selecione o repositório
3. Em "Main file path", coloque: `app/main.py`
4. Em "Secrets", adicione sua chave da API
5. Deploy — você recebe uma URL pública gratuita

---

## DIA 11 — README e documentação final

```markdown
# Crescimento para quem?
### Estrutura empresarial e distribuição de riqueza nos municípios de São Paulo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://SEU-APP.streamlit.app)

## A pergunta
São Paulo é o estado mais rico do Brasil. Mas essa riqueza está distribuída como?
Municípios com mais empresas são necessariamente mais ricos?
E quando são mais ricos, essa riqueza chega para a população?

## O que este projeto entrega
Um app web interativo onde qualquer pessoa pode:
- Explorar os 645 municípios paulistas por riqueza, estrutura empresarial e tipologia
- Ver a composição setorial do PIB de cada município
- Digitar um CNPJ e receber uma análise do município onde a empresa opera,
  gerada por IA com base em dados reais

## Principais achados
- A correlação entre número de empresas e PIB per capita é [X] — mais fraca
  do que o senso comum sugere
- Municípios com alta proporção de MEIs tendem a ter PIB per capita [X]% menor,
  sugerindo empreendedorismo de subsistência, não de geração de riqueza
- [N] municípios foram classificados como "Rico Concentrado" — PIB per capita
  alto mas estrutura empresarial frágil, dependente de grandes instalações industriais
- [N] municípios têm mais de 40% do PIB gerado pelo setor público

## Tecnologias
| Tecnologia | Uso |
|---|---|
| Python + Pandas | Pipeline de dados e transformações |
| DuckDB | Queries analíticas nos dados processados |
| Plotly | Gráficos interativos |
| Streamlit | Interface web e deploy |
| BrasilAPI | Dados de CNPJ (gratuita) |
| Claude API | Análise em linguagem natural |

## Limitações
- O PIB Municipal (SEADE) vai até 2020; os dados de empresas são de 2024/2025.
  A comparação temporal tem limitações que são reconhecidas na análise.
- PIB per capita é uma proxy imperfeita para bem-estar — não captura distribuição de renda.
- Municípios com grandes plantas industriais têm PIB per capita distorcido para cima.

## Como reproduzir localmente
```bash
git clone https://github.com/st-ricardof/sp-crescimento-para-quem
cd sp-crescimento-para-quem
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Baixe os dados nas URLs indicadas acima e salve em data/raw/
# Execute os notebooks em ordem (01 → 03) para gerar data/processed/dataset_base.csv
# Crie um arquivo .env com sua chave da API Claude

streamlit run app/main.py
```

## Autor
Ricardo Santos · [LinkedIn](https://linkedin.com/in/st-ricardof)
```

---

## Checklist final de publicação

### Código e qualidade
- [ ] `data/raw/` está no `.gitignore` e não foi commitado
- [ ] `.env` está no `.gitignore` e não foi commitado
- [ ] Todos os notebooks executam sem erro do início ao fim
- [ ] O app Streamlit roda localmente sem erros
- [ ] O app faz o deploy no Streamlit Cloud sem erros

### Documentação
- [ ] README preenchido com os achados reais (números dos dados)
- [ ] Seção de limitações escrita com honestidade
- [ ] Link do app no badge do README
- [ ] Screenshots do app no README (tira prints e adiciona como imagem)

### Divulgação
- [ ] Repositório público no GitHub com nome descritivo
- [ ] Link do repositório adicionado ao LinkedIn
- [ ] Link do app ao vivo adicionado ao LinkedIn
- [ ] Post no LinkedIn contando o projeto (o recrutador busca isso)

---

## O que este projeto demonstra para recrutadores

| Competência | Como aparece no projeto |
|---|---|
| Merge de múltiplas fontes | 3 bases públicas conectadas por chave municipal |
| SQL analítico | DuckDB com queries reais, não só pandas |
| Limpeza de dados governamentais | Tratamento de encoding, formatos de código IBGE |
| Estatística aplicada | Correlação, HHI, análise de quartis |
| Pensamento analítico | Questiona causalidade, não aceita correlação como resposta |
| Integração de APIs | CNPJ (Receita Federal) + IA (Claude) |
| Engenharia de software básica | Separação de responsabilidades, cache, variáveis de ambiente |
| Produto, não exercício | App ao vivo com URL pública, não notebook local |
| Honestidade metodológica | Seção de limitações explícita no README e no app |
| Contexto além dos dados | Explica o que está por trás dos números |

---

## Uma nota sobre o que diferencia este projeto

A maioria dos portfólios de Data Analyst é uma pasta com notebooks e gráficos estáticos.
Este projeto é um **produto funcional** — tem URL, tem interatividade, tem IA integrada.

Quando um recrutador digitar o CNPJ da própria empresa dele e receber uma análise
do município onde ela opera, o projeto vira uma demonstração de capacidade real,
não de intenção acadêmica.

Isso é memorável. É disso que se trata um portfólio de destaque.

---

*Roteiro criado para Ricardo Fernando dos Santos — busca de emprego 2025*
