"""
Etapa 2 do pipeline — Tratamento (Pandas).

Lê o CSV bruto (dados/livros_brutos.csv — ou o de exemplo, como
fallback, se o real ainda não existir), limpa os tipos e cria a coluna
alvo para o modelo. Salva em dados/livros_tratados.csv.

Rode: python tratamento/tratar_dados.py
"""
from pathlib import Path

import pandas as pd

DADOS_DIR = Path(__file__).parent.parent / "dados"
BRUTO_REAL = DADOS_DIR / "livros_brutos.csv"
BRUTO_EXEMPLO = DADOS_DIR / "livros_brutos_exemplo.csv"
SAIDA = DADOS_DIR / "livros_tratados.csv"

MAPA_ESTRELAS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def carregar_bruto() -> pd.DataFrame:
    if BRUTO_REAL.exists():
        print(f"usando dados reais: {BRUTO_REAL}")
        return pd.read_csv(BRUTO_REAL)

    print(f"aviso: {BRUTO_REAL.name} não encontrado — usando dados de exemplo ({BRUTO_EXEMPLO.name}).")
    print("       rode coleta/coletor.py para gerar os dados reais.")
    return pd.read_csv(BRUTO_EXEMPLO)


def tratar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # "£51.77" -> 51.77
    df["preco"] = df["preco_texto"].str.replace("£", "", regex=False).astype(float)

    # "Three" -> 3
    df["estrelas"] = df["estrelas_texto"].map(MAPA_ESTRELAS)

    # coluna-alvo para o modelo de classificação
    df["bem_avaliado"] = (df["estrelas"] >= 4).astype(int)

    df = df.drop(columns=["preco_texto", "estrelas_texto"])
    df = df.dropna(subset=["preco", "estrelas"])
    df = df.drop_duplicates(subset=["titulo", "categoria"])

    return df[["titulo", "categoria", "preco", "estrelas", "bem_avaliado"]]


def main():
    df_bruto = carregar_bruto()
    df_tratado = tratar(df_bruto)

    df_tratado.to_csv(SAIDA, index=False)
    print(f"{len(df_tratado)} livros tratados salvos em: {SAIDA}")
    print(f"Taxa de 'bem avaliado' (4-5 estrelas): {df_tratado['bem_avaliado'].mean():.1%}")


if __name__ == "__main__":
    main()
