"""
Etapa 1 do pipeline — Coleta (Playwright).

Percorre várias categorias do books.toscrape.com e salva um CSV "bruto"
(sem tratamento) em dados/livros_brutos.csv. A etapa de tratamento
(tratamento/tratar_dados.py) é responsável por limpar isso depois —
de propósito, para separar bem as responsabilidades do pipeline.

Rode: python coleta/coletor.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = "http://books.toscrape.com/catalogue/category/books/{slug}/index.html"

# categoria -> slug usado na URL do site
CATEGORIAS = {
    "Travel": "travel_2",
    "Mystery": "mystery_3",
    "Historical Fiction": "historical-fiction_4",
    "Classics": "classics_6",
    "Poetry": "poetry_23",
    "Romance": "romance_8",
    "Science Fiction": "science-fiction_16",
    "Fantasy": "fantasy_19",
}

SAIDA = Path(__file__).parent.parent / "dados" / "livros_brutos.csv"


def coletar_categoria(pagina, categoria: str, slug: str) -> list[dict]:
    """Coleta todos os livros de uma categoria, percorrendo a paginação."""
    livros = []
    url = BASE_URL.format(slug=slug)

    while url:
        pagina.goto(url, timeout=15_000)
        cards = pagina.locator(".product_pod").all()

        for card in cards:
            titulo = card.locator("h3 a").get_attribute("title")
            preco_texto = card.locator(".price_color").inner_text()
            classe_estrela = card.locator(".star-rating").get_attribute("class")
            estrelas_texto = classe_estrela.replace("star-rating", "").strip()

            livros.append(
                {
                    "titulo": titulo,
                    "preco_texto": preco_texto,
                    "estrelas_texto": estrelas_texto,
                    "categoria": categoria,
                }
            )

        proximo = pagina.locator("li.next a")
        if proximo.count() > 0:
            href = proximo.get_attribute("href")
            url = url.rsplit("/", 1)[0] + "/" + href
        else:
            url = None

    return livros


def main():
    todos_os_livros = []

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()

        for categoria, slug in CATEGORIAS.items():
            print(f"coletando categoria: {categoria}...")
            livros = coletar_categoria(pagina, categoria, slug)
            todos_os_livros.extend(livros)
            print(f"  {len(livros)} livros coletados")

        navegador.close()

    import csv

    with open(SAIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=todos_os_livros[0].keys())
        writer.writeheader()
        writer.writerows(todos_os_livros)

    print(f"\nTotal: {len(todos_os_livros)} livros salvos em {SAIDA}")


if __name__ == "__main__":
    main()
