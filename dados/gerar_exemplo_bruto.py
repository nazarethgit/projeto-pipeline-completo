"""
Gera dados/livros_brutos_exemplo.csv — um substituto para a saída real
do coletor.py, no MESMO formato (colunas e valores brutos, tipo
"£51.77" e "Three"), com uma relação causal simulada entre preço e
avaliação (para o modelo da etapa 3 ter algo real para aprender).

Isso existe para você conseguir testar e demonstrar o pipeline inteiro
mesmo sem internet ou antes de rodar o coletor.py de verdade. Quando
rodar o coletor.py, o dados/livros_brutos.csv real passa a ser
usado automaticamente no lugar deste.

Rode: python dados/gerar_exemplo_bruto.py
"""
import csv
import random
from pathlib import Path

random.seed(7)

ESTRELAS_TEXTO = ["One", "Two", "Three", "Four", "Five"]
CATEGORIAS = [
    "Travel", "Mystery", "Historical Fiction", "Classics",
    "Poetry", "Romance", "Science Fiction", "Fantasy",
]
QUANTIDADE_POR_CATEGORIA = 30

SAIDA = Path(__file__).parent / "livros_brutos_exemplo.csv"


def gerar_estrelas(preco: float, categoria: str) -> int:
    """Simula uma relação: livros mais caros e de certas categorias
    tendem a ter avaliação um pouco melhor (mas com bastante ruído)."""
    base = 2.5
    base += (preco / 60)                       # livro mais caro, nota um pouco maior
    base += 0.6 if categoria in ("Classics", "Poetry") else 0
    base += random.uniform(-1.5, 1.5)           # ruído — não é determinístico
    estrelas = round(min(max(base, 1), 5))
    return estrelas


def gerar_livro(i: int, categoria: str) -> dict:
    preco = round(random.uniform(10, 60), 2)
    estrelas = gerar_estrelas(preco, categoria)

    return {
        "titulo": f"{categoria} Book {i}",
        "preco_texto": f"£{preco:.2f}",
        "estrelas_texto": ESTRELAS_TEXTO[estrelas - 1],
        "categoria": categoria,
    }


def main():
    livros = []
    for categoria in CATEGORIAS:
        for i in range(1, QUANTIDADE_POR_CATEGORIA + 1):
            livros.append(gerar_livro(i, categoria))

    with open(SAIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=livros[0].keys())
        writer.writeheader()
        writer.writerows(livros)

    print(f"{len(livros)} livros de exemplo gerados em: {SAIDA}")


if __name__ == "__main__":
    main()
