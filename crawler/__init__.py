from selenium import webdriver
import selenium
import selenium.webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

from crawler import soupr
from .logger import logger
import time
from bs4 import BeautifulSoup

__all__ = ["get_page", "extract"]

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--start-fullscreen")

driver = None


def hello_world():
    print("Hello, world!")


def year_extract(year: str) -> str:
    if ":" in year:
        start_year, end_year = year.split(":")
        start_year = int(start_year)
        end_year = int(end_year)
        year_range = [str(year) for year in range(start_year, end_year + 1)]
    else:
        year_range = [year]

    return year_range


def extract_citation_counts(article_soup):
    """
    Extract citation counts per year from an article page.

    Args:
        article_soup: BeautifulSoup object of the article page

    Returns:
        dict: Dictionary mapping years to citation counts
    """
    citation_data = {}

    # Find the citation graph
    citation_bars = article_soup.select("#gsc_oci_graph_bars .gsc_oci_g_a")

    # If no citation graph is found, return empty dict
    if not citation_bars:
        return citation_data

    # Extract year and citation count from each bar
    for bar in citation_bars:
        year = None
        count = None

        # Extract year from the href attribute (as_ylo and as_yhi parameters)
        href = bar.get("href", "")
        year_match = href.find("as_ylo=")
        if year_match != -1:
            year = href[year_match + 7 : year_match + 11]

        # Extract count from the span element
        count_elem = bar.select_one(".gsc_oci_g_al")
        if count_elem:
            count = count_elem.text.strip()

        if year and count:
            citation_data[year] = int(count)

    return citation_data


def get_article_page(driver, article_url):
    """
    Navigate to an article page and return its soup.

    Args:
        driver: Selenium webdriver instance
        article_url: URL of the article

    Returns:
        BeautifulSoup object of the article page
    """
    try:
        driver.get(article_url)

        # Wait for the citation information to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "gsc_oci_value"))
        )

        # Get the page source and parse with BeautifulSoup
        page_source = driver.page_source
        return BeautifulSoup(page_source, "html.parser")
    except Exception as e:
        logger.error(f"Error loading article page: {str(e)}")
        return None


def extract_citations(scholar_id, articles, target_years):
    """
    Extract citation data for a list of articles.

    Args:
        scholar_id: Google Scholar ID of the author
        articles: List of article dictionaries with title, url, and year
        target_years: List of years for which to extract citation data

    Returns:
        list: List of lists with citation data in format
             [scholar_id, title, pub_year, citation_year1, citation_year2, ...]
    """
    global driver
    citation_data = []

    try:
        if driver is None:
            driver = initialize_driver()

        for article in articles:
            title = article["title"]
            url = article["url"]
            pub_year = article["year"]

            logger.info(f"Extracting citation data for article: {title}")

            row_data = [scholar_id, title, pub_year]

            # Get the article page
            article_soup = get_article_page(driver, url)
            if article_soup is None:
                # Add -1 for each target year if article page couldn't be loaded
                row_data.extend([-1] * len(target_years))
                citation_data.append(row_data)
                continue

            # Extract citation counts
            citation_counts = extract_citation_counts(article_soup)

            # Add citation counts for each target year
            for year in target_years:
                row_data.append(citation_counts.get(year, -1))

            citation_data.append(row_data)

            # Add a small delay to avoid overwhelming the server
            time.sleep(1)

    except Exception as e:
        logger.error(f"Error extracting citation data: {str(e)}")
    finally:
        # Don't close driver here as it's managed by the calling function
        pass

    return citation_data


def ensure_xlsx_extension(save_path: str) -> str:
    """Ensure the save path has a .xlsx extension."""
    if not save_path.lower().endswith(".xlsx"):
        save_path += ".xlsx"
    return save_path


def exit_driver():
    """Properly exit and clean up the driver."""
    global driver
    if driver:
        try:
            driver.quit()
            logger.info("WebDriver successfully closed")
        except Exception as e:
            logger.error(f"Error closing WebDriver: {str(e)}")
        finally:
            driver = None


def extract(
    scholar_id: str,
    year: str,
    save_path: str,
    overwrite: bool,
):
    year_range = year_extract(year)
    page_src = get_page(scholar_id)
    articles_to_find = soupr.get_articles(page_src, year_range)
    logger.info(f"Found {len(articles_to_find)} articles for the year(s) {year_range}.")

    # Extract citation data for all articles
    citation_data = extract_citations(scholar_id, articles_to_find, year_range)

    # Write citation data to CSV
    if citation_data:
        import pandas as pd

        # Create column headers
        headers = ["scholar_id", "title", "publication_year"]
        headers.extend([f"citations_{year}" for year in year_range])

        df = pd.DataFrame(citation_data, columns=headers)
        logger.info(
            f"DataFrame created with {len(df)} rows and {len(df.columns)} columns."
        )

        # Call function to save DataFrame to Excel
        save_to_excel(df, save_path, overwrite)

    # Ensure driver is properly closed
    exit_driver()


def save_to_excel(df, save_path, overwrite=False):
    """
    Save a DataFrame to an Excel file.

    Args:
        df: Pandas DataFrame to save
        save_path: Path where to save the file
        overwrite: Whether to overwrite if file exists

    Returns:
        str: Path where the file was saved
    """
    import os

    # Ensure the save path has a .xlsx extension
    save_path = ensure_xlsx_extension(save_path)

    # If save_path is just a filename without a directory, save in output folder
    if os.path.dirname(save_path) == "":
        save_path = os.path.join("output", save_path)

    # Check if file exists and handle overwriting
    if os.path.exists(save_path) and not overwrite:
        # Generate a new filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Split the path to get directory and filename
        dir_path = os.path.dirname(save_path)
        file_name = os.path.basename(save_path)

        # Split the filename to get name and extension
        name_part, ext_part = os.path.splitext(file_name)

        # Create new filename with timestamp
        new_file_name = f"{name_part}_{timestamp}{ext_part}"

        # Create new save path
        save_path = os.path.join(dir_path, new_file_name)

        logger.info(
            f"File exists and overwrite=False. Generating new file name: {save_path}"
        )

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    # Save to Excel file
    df.to_excel(save_path, index=False)
    logger.info(f"Data saved to {save_path}")

    return save_path


def initialize_driver():
    """Initialize and return a new Chrome webdriver instance."""
    logger.info("Initializing Chrome webdriver")
    return selenium.webdriver.Chrome(options=chrome_options)


def navigate_to_scholar_profile(driver, scholar_id):
    """Navigate to the Google Scholar profile for the given ID."""
    driver.get(f"https://scholar.google.com/citations?user={scholar_id}&hl=en")
    logger.info(f"Accessing Google Scholar profile for ID: {scholar_id}")


def wait_for_page_load(driver, timeout):
    """Wait for the page to load completely."""
    try:
        # Wait for profile header to be present - indicates profile loaded
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "gsc_prf_w"))
        )
        logger.info("Page fully loaded")
        return True
    except TimeoutException:
        logger.warning(f"Timed out waiting for page to load after {timeout} seconds")
        return False


def scroll_page(driver, scroll_height=300, max_scrolls=10):
    """Scroll the page naturally."""
    logger.info("Starting to scroll down naturally")
    for i in range(max_scrolls):
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(0.5)  # Small delay to make scrolling look natural
    logger.info("Scrolling complete")


def click_show_more_button(driver):
    """Click the 'Show more' button until it's disabled."""
    logger.info("Starting to click 'Show more' button")
    while True:
        try:
            # Find the button
            show_more_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "gsc_bpf_more"))
            )

            # Check if button is disabled
            if show_more_button.get_attribute("disabled"):
                logger.info("'Show more' button is now disabled, stopping clicks")
                break

            # Scroll to the button to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            time.sleep(0.5)

            # Click the button
            show_more_button.click()
            logger.info("Clicked 'Show more' button")

            # Wait for new content to load
            time.sleep(2)

        except (
            TimeoutException,
            ElementClickInterceptedException,
            StaleElementReferenceException,
        ) as e:
            logger.warning(f"Exception while trying to click 'Show more': {str(e)}")
            break

    logger.info("Finished clicking 'Show more' button")


def save_html_to_file(soup, scholar_id, output_path="output", filename=None):
    """
    Save BeautifulSoup HTML to a file.

    Args:
        soup: BeautifulSoup object containing the HTML
        scholar_id: Google Scholar ID for filename generation
        output_path: Directory path to save the HTML file
        filename: Custom filename (if None, will be generated from scholar_id)

    Returns:
        The path to the saved file
    """
    import os
    from datetime import datetime

    # Create output directory if it doesn't exist
    if output_path and not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scholar_{scholar_id}_{timestamp}.html"

    # Create full file path
    file_path = os.path.join(output_path, filename) if output_path else filename

    # Save the prettified HTML
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    logger.info(f"HTML saved to {file_path}")
    return file_path


def get_page_source(driver):
    """Get the page source and parse with BeautifulSoup."""
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # url = driver.current_url
    # scholar_id = url.split("user=")[1].split("&")[0] if "user=" in url else "unknown"
    # save_html_to_file(soup, scholar_id)
    return soup


def cleanup_driver(driver_instance):
    """Clean up the driver instance."""
    global driver
    if driver_instance:
        driver_instance.quit()
        if driver_instance is driver:
            driver = None


def get_page(
    scholar_id: str,
    timeout: int = 30,
    save_html: bool = False,
    output_path: str = "",
    filename: str = None,
) -> str:
    """
    Get the page source for a Google Scholar profile.

    Args:
        scholar_id: Google Scholar ID
        timeout: Timeout for page loading
        save_html: Whether to save the HTML to file
        output_path: Directory path to save the HTML file
        filename: Custom filename (if None, will be generated from scholar_id)

    Returns:
        The page source as a string
    """
    global driver
    page_source = None

    try:
        if driver is None:
            driver = initialize_driver()

        navigate_to_scholar_profile(driver, scholar_id)

        if wait_for_page_load(driver, timeout):
            scroll_page(driver)
            click_show_more_button(driver)
            page_source = get_page_source(driver)

    except Exception as e:
        logger.error(f"Error while getting page: {str(e)}")
    finally:
        cleanup_driver(driver)

    return page_source
