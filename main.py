from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Configuration
BASE_URL = "https://moodle.vse.cz"
COURSE_URL = f"{BASE_URL}/course/view.php?id=13407&breadcrumb=1"  # Replace with your course ID
DOWNLOAD_DIR = "downloads"  # Folder to save the course files
MOODLE_SESSION_COOKIE = "3us4a9beuf6ii7efg6ges388ph"  # Replace with your MoodleSession cookie

# Create download directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

# Inject the MoodleSession cookie
driver.get(BASE_URL)
driver.add_cookie({
    'name': 'MoodleSession',
    'value': MOODLE_SESSION_COOKIE,
    'domain': 'moodle.vse.cz'
})

# Navigate to the course
driver.get(COURSE_URL)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "topics")))

# Extract section links
sections = driver.find_elements(By.CSS_SELECTOR, "ul.topics li a")
section_links = [section.get_attribute('href') for section in sections]

# Loop through each section
for link in section_links:
    driver.get(link)
    time.sleep(2)

    # Wait for the content section to load
    try:
        region_main = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "region-main"))
        )
        section_content = region_main.get_attribute('outerHTML')

        # Create folder based on section title
        section_title = driver.find_element(By.CSS_SELECTOR, "h2.pcrgrid_course_heading").text
        folder_path = os.path.join(DOWNLOAD_DIR, section_title)
        os.makedirs(folder_path, exist_ok=True)

        # Save the content to an HTML file
        filename = os.path.join(folder_path, "index.html")
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(section_content)

        print(f"Downloaded section: {section_title}")

    except Exception as e:
        print(f"Failed to download content from {link}: {str(e)}")

# Close the driver
driver.quit()
print("Crawling complete!")
