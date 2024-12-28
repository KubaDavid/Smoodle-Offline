import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Load environment variables
load_dotenv()

# Configuration
DOMAIN = os.getenv("DOMAIN", "moodle.vse.cz")
COURSE_URL = f"https://{DOMAIN}/course/view.php?id={os.getenv('COURSE_ID')}&breadcrumb=1"
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")  # Folder to save the course files
MOODLE_SESSION_COOKIE = os.getenv("MOODLE_SESSION_COOKIE")

# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu") # Chromedriver has some issues in WSL so this fixes it
driver = webdriver.Chrome(options=options)

# Inject the MoodleSession cookie
driver.get(f"https://{DOMAIN}")
driver.add_cookie({
    'name': 'MoodleSession',
    'value': MOODLE_SESSION_COOKIE,
    'domain': DOMAIN
})

# Navigate to the course
driver.get(COURSE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "topics")))

# Extract section links and remove duplicates
sections = driver.find_elements(By.CSS_SELECTOR, "ul.topics li a")
section_links = list(dict.fromkeys([section.get_attribute('href') for section in sections]))

print("Course Structure:")
for idx, link in enumerate(section_links):
    print(f"[{idx+1}] {link}")

# Initialize combined HTML
combined_html = '<html><head><title>Course Content</title></head><body>'

# Loop through each section (Level 1: Sections)
for idx, link in enumerate(section_links):
    print(f"Processing section {idx+1}/{len(section_links)}: {link}")
    driver.get(link)
    time.sleep(2)

    # Wait for the content section to load
    try:
        region_main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "region-main"))
        )
        section_content = region_main.get_attribute('outerHTML')

        # Add section to combined HTML
        section_title = driver.find_element(By.CSS_SELECTOR, "h2.pcrgrid_course_heading").text
        combined_html += f'<h1>{section_title}</h1>'
        combined_html += section_content

        print(f"Downloaded section: {section_title}")

        # Check for links to parts within the section (Level 2: Parts)
        part_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/mod/"]')
        for part_idx, part_link in enumerate(part_links):
            part_url = part_link.get_attribute('href')
            print(f"  Part {part_idx+1}/{len(part_links)}: {part_url}")
            driver.get(part_url)
            time.sleep(2)

            # If part is a book, process chapters (Level 3: Chapters)
            if '/book/' in part_url:
                book_title = driver.find_element(By.CSS_SELECTOR, "h2").text
                combined_html += f'<h2>{book_title}</h2>'

                # Save the book's initial content
                book_content = driver.find_element(By.ID, "region-main").get_attribute('outerHTML')
                combined_html += book_content

                print(f"Downloaded book: {book_title}")

                # Gather all chapter links once to avoid stale references
                chapter_links = [link.get_attribute('href') for link in driver.find_elements(By.CSS_SELECTOR, 'div.book_toc ul li a')]
                print(f"  Found {len(chapter_links)} chapters in book {book_title}.")

                # Process each chapter
                for chapter_idx, chapter_url in enumerate(chapter_links):
                    try:
                        print(f"    Chapter {chapter_idx+1}/{len(chapter_links)}: {chapter_url}")
                        driver.get(chapter_url)
                        time.sleep(2)

                        # Save chapter content
                        chapter_content = driver.find_element(By.ID, "region-main").get_attribute('outerHTML')
                        chapter_title = driver.find_element(By.TAG_NAME, "h2").text
                        combined_html += f'<h3>{chapter_title}</h3>'
                        combined_html += chapter_content

                        print(f"    Downloaded chapter: {chapter_title}")
                    except Exception as e:
                        print(f"    Failed to download chapter {chapter_idx+1}: {str(e)}")
            else:
                print(f"  Skipping non-book part: {part_url}")

    except Exception as e:
        print(f"Failed to download content from {link}: {str(e)}")

# Close the driver
driver.quit()

# Finalize and save combined HTML
combined_html += '</body></html>'
combined_file = os.path.join(DOWNLOAD_DIR, 'combined_course_content.html')
with open(combined_file, 'w', encoding='utf-8') as file:
    file.write(combined_html)

print("Crawling complete! Combined content saved.")
