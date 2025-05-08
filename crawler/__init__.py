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
from .logger import logger
import time
from bs4 import BeautifulSoup

__all__ = ["get_page", "extract"]

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")
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


def extract(scholar_id: str, year: str, verbose: bool, save_path: str, overwrite: bool):
    year_ex = year_extract(year)
    page_src = get_page(scholar_id)

    return "hi"


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

    url = driver.current_url
    scholar_id = url.split("user=")[1].split("&")[0] if "user=" in url else "unknown"
    save_html_to_file(soup, scholar_id)


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
