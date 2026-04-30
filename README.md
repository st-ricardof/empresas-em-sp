# 📊 Estrutura Empresarial e Desenvolvimento Municipal de São Paulo

**A quantidade de empresas explica o desenvolvimento de um município?**  
Análise com dados dos 645 municípios paulistas sugere que não — e aponta o que importa mais.

> 🔗 Dashboard interativo: **https://empresas-vs-ipdm-sp.streamlit.app/**

---

##  Resumo 

Este projeto investiga a relação entre estrutura empresarial e desenvolvimento socioeconômico (IPDM) nos municípios de São Paulo.

**Principais insights:**
- O **volume total de empresas não explica desenvolvimento** (correlação: **0,03**)
- Municípios com maior proporção de **MEIs tendem a ter menor IPDM** (correlação: **-0,38**)
- **Escolaridade** apresenta relação muito mais forte com desenvolvimento (correlação: **0,76**)

 **Conclusão:** o nível de desenvolvimento está mais associado à **estrutura econômica e fatores sociais** do que à quantidade de empresas.

---

##  Por que isso importa

Os dados sugerem que políticas focadas apenas na abertura de empresas podem ter impacto limitado no desenvolvimento local.

- Incentivar **crescimento além do MEI** pode ser mais relevante do que aumentar volume de negócios  
- A **qualidade da estrutura produtiva** importa mais do que sua quantidade  
- **Educação** aparece como fator central no desenvolvimento municipal  

---

##  Principais achados

| Relação | Correlação | Interpretação |
|---|---|---|
| % MEI × IPDM | **-0,38** | Maior presença de MEIs associada a menor desenvolvimento |
| % Pequenas empresas × Riqueza | **+0,36** | Pequenas empresas têm associação mais positiva que MEIs |
| Escolaridade × IPDM | **+0,76** | Fator mais fortemente associado ao desenvolvimento |
| Total de empresas × IPDM | **+0,03** | Volume praticamente irrelevante |
| % Microempresas × % Demais | **-0,93** | Estrutura empresarial é altamente concentrada |

Além disso:
- **91,2% das empresas são microempresas**
- **12,5% operam como MEI**

---

##  Abordagem analítica

- Análise exploratória (EDA)
- Cálculo de correlações entre variáveis
- Comparação entre estrutura empresarial e indicadores de desenvolvimento
- Análise territorial (mapa + distribuição espacial)

---

##  O dashboard

O dashboard foi desenvolvido para permitir exploração intuitiva dos dados em três níveis:

**Visão geral**  
Panorama do estado com indicadores principais (população, empresas, estrutura e IPDM)

**Distribuição territorial**  
Mapa interativo dos municípios com múltiplas camadas de análise

**Relação entre variáveis**  
Scatter plot dinâmico com seleção de eixos e linha de tendência

Um diferencial do projeto foi a criação de um **dicionário interpretativo** com mais de 50 combinações de variáveis, traduzindo correlações em linguagem acessível.

---

## 📸 Prints

> 📌 Adicionar após deploy:
- visão geral
- mapa
- scatter (% MEI vs IPDM)

---

##  Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3.11 |
| Banco de dados | DuckDB |
| Análise | Pandas, NumPy |
| Visualização | Plotly, GeoPandas |
| Geografia | geobr |
| Dashboard | Streamlit |
| Notebooks | Jupyter |

---

## 📁 Estrutura do projeto

```
empresas-em-sp/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_exploracao.ipynb
│   └── 02_geografia.ipynb
│
├── app/
│   └── app.py
│
└── outputs/
```

---

## 🔄 Como reproduzir localmente

```bash
git clone https://github.com/st-ricardof/empresas-em-sp
cd empresas-em-sp

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# baixar dados em data/raw/

streamlit run app/app.py
```

---

## ⚠️ Limitações

- Correlação não implica causalidade  
- Bases com anos distintos (2022–2026)  
- Ausência de variáveis estruturais adicionais (ex: renda detalhada, infraestrutura)  
- Análise descritiva (não preditiva)

---

# Bastidores do projeto 

## Como surgiu o problema

A motivação inicial foi explorar dados abertos do estado de São Paulo, pouco utilizados em portfólios.

A pergunta central emergiu a partir do **Painel de Empresas da SEADE**:

> Municípios com mais empresas são necessariamente mais desenvolvidos?

Inicialmente, considerei o PIB municipal como indicador de desenvolvimento. No entanto, a defasagem temporal (2020 vs 2026) comprometeria a análise.

A solução foi utilizar o **IPDM**, indicador mais recente e multidimensional.

---

## A hipótese — e o que os dados mostraram

Hipótese inicial:

> Mais empresas → mais desenvolvimento

Resultado:

- O volume de empresas praticamente **não tem relação com desenvolvimento**
- A estrutura empresarial também não mostrou efeitos fortes isoladamente
- A relação mais consistente encontrada foi entre **alta proporção de MEIs e menor IPDM**

---

## Interpretação dos resultados

O projeto não encontrou um “driver único” de desenvolvimento.

Pelo contrário, os dados indicam que:
- desenvolvimento é multifatorial  
- variáveis sociais (como educação) têm maior peso  
- estrutura produtiva importa mais do que volume  

Em vez de confirmar a hipótese inicial, a análise mostrou seus limites — o que também é um resultado relevante.

---

## Reflexões finais

Este projeto é intencionalmente **descritivo**.

Ele não busca prever ou explicar causalmente, mas sim:
- identificar padrões
- levantar hipóteses
- apoiar discussões mais informadas

> Em alguns casos, a principal descoberta é justamente a ausência de uma relação forte — e isso também orienta melhores decisões.

---

##  Dados utilizados

| Dataset | Fonte | Ano |
|---|---|---|
| Painel de Empresas SP | SEADE | 2026 |
| IPDM | SEADE | 2025 |
| Censo Demográfico | IBGE | 2022 |

---

## 👤 Autor

**Ricardo Fernando dos Santos**  
São Paulo, Brasil

- GitHub: https://github.com/st-ricardof  
- LinkedIn: https://www.linkedin.com/in/st-ricardof/  
- Email: st.ricardof@gmail.com
