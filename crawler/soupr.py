from bs4 import BeautifulSoup


def open_html(html_file_path):
    """Open an HTML file and return its content."""
    with open(html_file_path, "r", encoding="utf-8") as file:
        html_content = file.read()
    return html_content


def get_articles(soup, years):
    """
    Extract paper titles and URLs from Google Scholar page for specific years.

    Args:
        html_path (str): Path to the HTML file
        years (list): List of years to filter by (e.g., ["2022", "2023"])

    Returns:
        list: List of dictionaries containing title, URL, and year for each matching article
    """
    articles = []

    # Find all article rows
    article_rows = soup.find_all("tr", class_="gsc_a_tr")

    for row in article_rows:
        # Get the year
        year_element = row.find("td", class_="gsc_a_y")
        if not year_element:
            continue

        year_span = year_element.find("span", class_="gsc_a_h")
        if not year_span:
            continue

        year = year_span.text.strip()

        # Check if the year is in the target years
        if year in years:
            # Get the title and URL
            title_column = row.find("td", class_="gsc_a_t")
            if not title_column:
                continue

            title_element = title_column.find("a", class_="gsc_a_at")
            if title_element:
                title = title_element.text.strip()
                url = title_element.get("href")
                if url:
                    # For Google Scholar, URLs are relative, so we need to add the base URL
                    if not url.startswith("http"):
                        url = "https://scholar.google.co.id" + url

                    articles.append({"title": title, "url": url, "year": year})

    return articles
