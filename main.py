import typer
from datetime import datetime

import crawler
from crawler import soupr
import crawler.soupr


def main(
    scholar_id: str = typer.Option(
        ...,  # Makes this parameter required
        "--scholar-id",
        "-s",
        help="Google Scholar profile ID to scrape (required).",
    ),
    year: str = typer.Option(
        f"{datetime.now().year}",
        "--year",
        "-y",
        help="Year range in YYYY format (single year) or YYYY:YYYY (range).",
    ),
    save_path: str = typer.Option(
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        "--save-path",
        "-o",
        help="Output file path. Defaults to current date/time if not specified.",
    ),
    overwrite: bool = typer.Option(
        False,
        "--overwrite",
        help="Overwrite output file if it exists.",
    ),
):
    """
    Scrape publication data from a Google Scholar profile for the specified year(s). The output will be saved to a text file containing publication details.\n\n
    Sapi V.0.1.0 -- https://wwww.github.com/hippocampa\n
    """
    crawler.extract(scholar_id, year, save_path, overwrite)
    # articles = crawler.soupr.get_articles(
    #     r"D:\0_Lab\akreditasi_TI\sapi\output\scholar_igzQmigAAAAJ_20250508_122223.html",
    #     ["2020"],
    # )
    # for article in articles:
    #     print(f"Title: {article['title']}")
    #     print(f"URL: {article['url']}")
    #     print("-" * 40)


if __name__ == "__main__":
    typer.run(main)
