# Šmoodle Crawler

## Overview
This tool is designed for students to download and organize course content from Moodle for offline reading. It uses Python with Selenium to crawl through Moodle course sections, parts, and chapters, and compiles all the downloaded content into a single, easy-to-navigate HTML file.

---

## Requirements
- Python 3.8 or higher
- Google Chrome installed
- Chromedriver compatible with your Chrome version

### Install dependencies from `requirements.txt`
```bash
pip install -r requirements.txt
```

---

## Setting Up the Environment
1. Create a `.env` file in the project directory with the following structure:
```
DOMAIN=moodle.domain.cz
COURSE_ID=123456
DOWNLOAD_DIR=downloads
MOODLE_SESSION_COOKIE=your-moodlesession-cookie-value
```
2. Replace `your-moodlesession-cookie-value` with your Moodle session cookie (see below for details).

---

## Obtaining the Moodle Session Cookie
### Steps to get the `MoodleSession` cookie:
1. Open your web browser (Chrome or Firefox) and log in to Moodle.
2. Right-click anywhere on the page and select **Inspect** (or press `F12`).
3. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox).
4. Under **Storage**, click **Cookies**.
5. Select your Moodle domain (e.g., `moodle.domain.cz`).
6. Look for the cookie named `MoodleSession`.
7. Copy the **Value** of the cookie.
8. Paste the value into your `.env` file like this:
```
MOODLE_SESSION_COOKIE=your_cookie_value_here
```

---

## Running the Script
```bash
python moodle_crawler_selenium.py
```

The script will:
1. Crawl through sections, parts, and chapters.
2. Download and organize the content.
3. Save all content into one HTML file named `combined_course_content.html` in the specified download directory.

---

## Output
- The combined HTML file can be found in the specified `DOWNLOAD_DIR`.
- It includes structured content with headings for sections, parts, and chapters.

---

## License
MIT License
