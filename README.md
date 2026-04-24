# 📊 Documentação — Análise da Base de Empresas (SP)

## 📌 Contexto

Esta etapa do projeto teve como objetivo compreender em profundidade a base de dados de empresas dos municípios do estado de São Paulo, antes de integrá-la a outras fontes.

A base foi obtida via SEADE (Fundação Sistema Estadual de Análise de Dados), com atualização mensal.

- **Data de download:** 06 de abril de 2026  
- **Fonte:** Cadastro Nacional de Pessoas Jurídicas (CNPJ) — Receita Federal  
- **Granularidade:** Empresas agregadas por município, setor, porte e regime fiscal  

---

## 🧠 Estrutura da base 

A base **não contém uma linha por empresa**, mas sim uma estrutura agregada.

Cada linha representa:

> quantidade de empresas com determinado perfil em um município

### Variáveis principais

| Variável | Descrição |
|---------|----------|
| `cod_munibge` | Código IBGE do município |
| `cod_classe` | Código CNAE (atividade econômica) |
| `cod_porte_empresa` | Porte da empresa |
| `opcao_mei` | Indica se a empresa é MEI |
| `empresas_ativas` | Quantidade de empresas naquele grupo |

---

## 🔍 Interpretação dos códigos

### Porte da empresa (`cod_porte_empresa`)

| Código | Categoria |
|-------|----------|
| 1 | Microempresa |
| 3 | Empresa de pequeno porte |
| 5 | Demais (média + grande) |

---

### Regime MEI (`opcao_mei`)

| Código | Significado |
|-------|------------|
| 1 | Sim (é MEI) |
| 2 | Não |
| 0 | Não se aplica |

---

## ⚠️ Distinção conceitual importante

- **MEI NÃO é um porte de empresa**
- MEI é um **regime fiscal**

Portanto:

- Toda MEI está dentro do universo de microempresas  
- Mas nem toda microempresa é MEI  

---

## 🔄 Transformações realizadas

A base foi transformada para permitir análise territorial (nível município).

### 1. Agregação por município

Foi criada uma base com:

- total de empresas  
- total de MEIs  
- percentual de MEIs  

---

### 2. Estrutura por porte

Foi construída uma tabela com:

- total de microempresas  
- total de pequenas empresas  
- total de empresas de maior porte  

E suas respectivas proporções dentro de cada município.

---

### 3. Validações realizadas

- Conferência de consistência entre totais agregados  
- Validação da granularidade da base  
- Cruzamento entre porte e regime MEI  

---

## 📊 Principais resultados

### Estrutura empresarial do estado

- ~95% das empresas são microempresas  
- ~1–2% são pequenas empresas  
- ~3–4% são empresas de maior porte  

👉 A estrutura produtiva é altamente pulverizada.

---

### Participação de MEI

- Média: ~12,5% das empresas  
- Variação: ~2,6% a ~22,5% entre municípios  

👉 Indica heterogeneidade territorial relevante.

---

### Relação entre MEI e microempresa

- Todas as MEIs estão dentro da categoria de microempresa  
- Apenas ~13,7% das microempresas são MEI  

👉 A maior parte das microempresas opera fora do regime simplificado.

---

## 🧠 Primeiras interpretações

A base sugere que:

- A economia paulista é majoritariamente composta por unidades produtivas de pequena escala  
- Existe diversidade dentro do universo das microempresas  
- A presença de MEI varia significativamente entre municípios  

Isso abre espaço para investigações como:

- diferenças territoriais na estrutura produtiva  
- relação entre escala econômica e geração de riqueza  
- padrões de formalização e informalidade  

---

## 🧭 Próximos passos

- Integração com base de PIB municipal  
- Construção de tipologia dos municípios  
- Análise da relação entre estrutura empresarial e renda  

---

## 💬 Observações finais

Esta etapa foi fundamental para:

- compreender a lógica da base  
- evitar interpretações incorretas  
- garantir consistência antes de cruzamento com outras fontes  

A abordagem adotada priorizou exploração e entendimento dos dados antes da definição rígida de hipóteses.