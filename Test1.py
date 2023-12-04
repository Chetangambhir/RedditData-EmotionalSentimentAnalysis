import time
from bs4 import BeautifulSoup
from selenium import webdriver

# Specify the path to the Chrome executable
chrome_binary_path = "C:\\Users\\PTI\\Downloads\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe"

# URL of the subreddit
url = "https://www.reddit.com/r/mentalhealth/"

# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chrome_binary_path

# Initialize a headless web browser with the specified options
driver = webdriver.Chrome(options=chrome_options)

# Send an HTTP GET request to the URL
driver.get(url)

# Scroll to the end of the page for 10 iterations
for _ in range(10):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)  # Wait for the page to load more content

# Parse the HTML content of the webpage
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all the <a> tags in the HTML
a_tags = soup.find_all('a', {'class': 'absolute inset-0'})

# Extract and print all the URLs
for a_tag in a_tags:
    url = a_tag.get('href')
    if url and '/r/mentalhealth/comments/' in url:  # Filter out non-post links
        print(url)

# Close the browser when you're done
driver.quit()
