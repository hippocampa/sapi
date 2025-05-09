import typer
from datetime import datetime
import os
from typing import Optional

import crawler


def main(
    scholar_id: Optional[str] = typer.Option(
        None,
        "--scholar-id",
        "-s",
        help="Google Scholar profile ID to scrape.",
    ),
    from_txt: Optional[str] = typer.Option(
        None,
        "--from-txt",
        "-f",
        help="Path to a text file containing Google Scholar IDs (one per line).",
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
    # Validate input parameters - either scholar_id or from_txt must be provided, but not both
    if scholar_id is None and from_txt is None:
        typer.echo("Error: Either --scholar-id or --from-txt must be provided.")
        raise typer.Exit(code=1)

    if scholar_id is not None and from_txt is not None:
        typer.echo("Error: --scholar-id and --from-txt cannot be used together.")
        raise typer.Exit(code=1)

    if from_txt is not None:
        # Process multiple scholar IDs from text file
        if not os.path.exists(from_txt):
            typer.echo(f"Error: File not found: {from_txt}")
            raise typer.Exit(code=1)

        try:
            with open(from_txt, "r") as file:
                scholar_ids = [line.strip() for line in file if line.strip()]

            if not scholar_ids:
                typer.echo(f"Error: No scholar IDs found in {from_txt}")
                raise typer.Exit(code=1)

            crawler.extract_from_txt(
                scholar_ids,
                year,
                save_path,
                overwrite,
            )

        except Exception as e:
            typer.echo(f"Error processing file {from_txt}: {str(e)}")
            raise typer.Exit(code=1)
    else:
        # Process single scholar ID
        crawler.extract(scholar_id, year, save_path, overwrite)


if __name__ == "__main__":
    typer.run(main)
