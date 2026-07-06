"""
Etapa 3 do pipeline — Modelo (Scikit-learn).

Treina um classificador para prever "bem_avaliado" (1 = 4-5 estrelas)
a partir de preço e categoria. Usa cross_val_predict para gerar uma
previsão para CADA livro sem vazamento de dados (a previsão de um
livro nunca vem de um modelo que o viu no treino) — assim o dashboard
mostra previsão vs. realidade de forma honesta, não só nos dados de
treino.

Também treina e salva um pipeline final (com todos os dados) em
modelo/pipeline_livros.pkl, para prever livros novos no futuro.

Rode: python modelo/aplicar_modelo.py
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DADOS_DIR = Path(__file__).parent.parent / "dados"
ENTRADA = DADOS_DIR / "livros_tratados.csv"
SAIDA_COM_PREVISOES = DADOS_DIR / "livros_com_previsoes.csv"
MODELO_PATH = Path(__file__).parent / "pipeline_livros.pkl"


def construir_pipeline() -> Pipeline:
    pre_processamento = ColumnTransformer(
        transformers=[
            ("preco", StandardScaler(), ["preco"]),
            ("categoria", OneHotEncoder(handle_unknown="ignore"), ["categoria"]),
        ]
    )
    return Pipeline(
        steps=[
            ("pre_processamento", pre_processamento),
            ("modelo", RandomForestClassifier(n_estimators=200, max_depth=5, random_state=42)),
        ]
    )


def main():
    df = pd.read_csv(ENTRADA)
    X = df[["preco", "categoria"]]
    y = df["bem_avaliado"]

    pipeline = construir_pipeline()

    # previsões "honestas" (out-of-fold) para todo o dataset
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    probabilidades = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")[:, 1]
    previsoes = (probabilidades >= 0.5).astype(int)

    print("Acurácia (out-of-fold):", round(accuracy_score(y, previsoes), 3))
    print("AUC-ROC (out-of-fold):", round(roc_auc_score(y, probabilidades), 3))

    df["probabilidade_bem_avaliado"] = probabilidades.round(3)
    df["previsto_bem_avaliado"] = previsoes
    df.to_csv(SAIDA_COM_PREVISOES, index=False)
    print(f"Dataset com previsões salvo em: {SAIDA_COM_PREVISOES}")

    # modelo final, treinado com todos os dados — para prever livros novos depois
    pipeline.fit(X, y)
    joblib.dump(pipeline, MODELO_PATH)
    print(f"Pipeline final salvo em: {MODELO_PATH}")


if __name__ == "__main__":
    main()
