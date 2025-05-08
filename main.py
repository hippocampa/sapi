import typer
from datetime import datetime

import crawler


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
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output with additional details.",
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
    crawler.extract(scholar_id, year, verbose, save_path, overwrite)

    # if verbose:
    #     typer.echo("Verbose mode enabled. Starting scraping process...")
    #     typer.echo(f"Target Scholar ID: {scholar_id}")
    #     typer.echo(f"Year range: {year}")
    #     typer.echo(f"Output will be saved to: {save_path}")
    #     typer.echo(f"Overwrite mode: {'enabled' if overwrite else 'disabled'}")

    # Your scraping logic would go here
    # typer.echo(f"Scraping data for Scholar ID: {scholar_id}, Year(s): {year}")
    # typer.echo(f"Results will be saved to: {save_path}")


if __name__ == "__main__":
    typer.run(main)
