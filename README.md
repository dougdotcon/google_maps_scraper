# Google Maps Lead Scraper

A robust Python automation tool for extracting business leads (contact information) from Google Maps. This project utilizes **Selenium** for automated navigation and **Tkinter** to provide a user-friendly graphical interface for configuration prior to execution.

## Features

-   **Graphical User Interface (GUI)**: Easily configure search parameters without touching the code.
-   **Multi-Keyword Search**: Accepts multiple search terms (e.g., "restaurants, pharmacies, lawyers") and executes searches sequentially.
-   **Customizable Location**: Sets the search center point using a full address.
-   **Data Extraction**: Collects business name, address, phone number, website, and Google Maps link.
-   **Result Limitation**: Set a maximum number of leads to scrape per search term.
-   **Excel Export**: Saves consolidated data into an `.xlsx` file with a timestamp to prevent overwriting.
-   **Headless Mode**: Option to run the browser in the background (invisible) for efficiency.

## Prerequisites

Ensure you have **Python 3.8+** installed on your system.

### Installation

1.  Clone this repository or download the source files.
2.  Install the required dependencies by running:

bash
pip install -r requirements.txt


The `requirements.txt` file includes:
-   `selenium`
-   `webdriver-manager`
-   `pandas`
-   `openpyxl`

## How to Use

1.  Run the main script:

bash
python scraper.py


2.  A configuration window will appear with the following fields:
    *   **Target Location**: The address where the search will be centered.
    *   **Search Terms**: Enter niches or keywords separated by commas (e.g., `marketing, consulting, design`).
    *   **Max Leads**: The number of results to fetch *for each term*.
    *   **Hidden Mode**: Check this option if you do not want to see the browser opening.

3.  Click **"Start Search"**.

4.  The system will:
    *   Open Google Maps.
    *   Search for the target address.
    *   Iterate over each keyword searching for nearby businesses.
    *   Extract available data.
    *   Save everything to an Excel file (e.g., `leads_marketing_167823.xlsx`) in the project folder.

## Project Structure

*   `scraper.py`: Main script containing the scraping logic and Tkinter interface.
    *   `browser.py`: Auxiliary module for managing the Selenium driver and Chrome settings.
    *   `requirements.txt`: List of required Python libraries.

## Notes

*   The script utilizes Google Chrome. Ensure the browser is installed.
*   Execution time depends on the number of terms and the lead limit configured.
*   Google Maps may present layout variations or rate limiting. The script includes `sleep` pauses to mitigate blocks, but excessive usage should be avoided.