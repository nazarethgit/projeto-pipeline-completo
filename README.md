# Projeto — Pipeline Ponta a Ponta: Coleta → Dashboard

Este é o projeto junta automação, tratamento
de dados, Machine Learning e visualização num pipeline só, com
responsabilidades bem separadas em 4 etapas.

**Pergunta que o pipeline responde:** dá pra prever se um livro será
bem avaliado (4-5 estrelas) só olhando o preço e a categoria?

## As 4 etapas

```
coleta/coletor.py            -> Playwright: raspa livros de 8 categorias do books.toscrape.com
tratamento/tratar_dados.py   -> Pandas: limpa tipos, cria a coluna-alvo (bem_avaliado)
modelo/aplicar_modelo.py     -> Scikit-learn: classifica e gera previsões sem vazamento de dados
dashboard/app.py             -> Streamlit: exibe tudo, com filtros e gráficos
```

Cada etapa lê o resultado da anterior via CSV em `dados/` — dá pra
rodar qualquer uma isoladamente, o que facilita debugar e também deixa
claro, numa entrevista, que você entende separação de responsabilidades
num pipeline de dados.

## Como rodar (em ordem)

```bash
pip install -r requirements.txt
playwright install chromium

# 1. coleta (real, precisa de internet)
python coleta/coletor.py

# 2. tratamento
python tratamento/tratar_dados.py

# 3. modelo
python modelo/aplicar_modelo.py

# 4. dashboard
streamlit run dashboard/app.py
```

## Rodando sem internet / antes de ter o coletor pronto

Incluí `dados/gerar_exemplo_bruto.py`, que gera um substituto do que o
coletor real produziria (mesmo formato, com uma relação causal
simulada e ruído entre preço/categoria e avaliação). Se
`dados/livros_brutos.csv` não existir, `tratar_dados.py` usa esse
arquivo de exemplo automaticamente (com um aviso no terminal) — assim
dá pra testar e demonstrar o pipeline inteiro mesmo sem ter rodado o
scraper ainda:

```bash
python dados/gerar_exemplo_bruto.py
python tratamento/tratar_dados.py
python modelo/aplicar_modelo.py
streamlit run dashboard/app.py
```

## Por que `cross_val_predict` em vez de treinar e prever nos mesmos dados

Se o modelo prevê os mesmos livros que usou para treinar, o resultado
fica bom demais e mentiroso (viu a resposta antes da prova). Por isso
`aplicar_modelo.py` usa `cross_val_predict`: cada livro só é previsto
por uma versão do modelo que **nunca o viu durante o treino**. É esse
número (honesto, ~0.61 de acurácia nos dados de exemplo) que aparece
no dashboard — não um número artificialmente perfeito.


