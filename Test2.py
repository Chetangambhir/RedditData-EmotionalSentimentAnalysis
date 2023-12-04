import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pytz
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import sqlite3

# Define a list of URLs
urls = [
    "https://www.reddit.com/r/mentalhealth/comments/17hl1ae/what_is_this_feeling_called_and_how_do_i_fix_it/",
"https://www.reddit.com/r/mentalhealth/comments/17hp71v/from_mental_wellbeing_to_performance_a_tale_of/",
"https://www.reddit.com/r/mentalhealth/comments/17hp5lp/is_there_a_term_for_this/",
"https://www.reddit.com/r/mentalhealth/comments/17hkw1y/i_need_help/",
"https://www.reddit.com/r/mentalhealth/comments/17hoz0u/do_it_all_for_love_or_just_let_go/",
"https://www.reddit.com/r/mentalhealth/comments/17hkcen/my_sort_of_friend_refuses_to_believe_counseling/",
"https://www.reddit.com/r/mentalhealth/comments/17hk924/i_gave_up_on_ed_recovery/",
"https://www.reddit.com/r/mentalhealth/comments/17hjsg9/cant_cope/",
"https://www.reddit.com/r/mentalhealth/comments/17hjqi8/impaired_memory_and_focus/",
"https://www.reddit.com/r/mentalhealth/comments/17hnbro/whats_it_like_having_a_boarderline_or_suspected/",
"https://www.reddit.com/r/mentalhealth/comments/17hn2sq/i_hateget_very_angry_and_impulsive_with_my/",
"https://www.reddit.com/r/mentalhealth/comments/17h3x3x/my_girlfriend_wakes_up_in_the_middle_of_the_night/",
"https://www.reddit.com/r/mentalhealth/comments/17hmgi7/thoughts_im_lost/",
"https://www.reddit.com/r/mentalhealth/comments/17hiyd8/i_need_someone_to_talk_too/",
"https://www.reddit.com/r/mentalhealth/comments/17hm9bf/bailed_on_job_interview/",
"https://www.reddit.com/r/mentalhealth/comments/17hdddl/im_45_only_just_realized_i_was_severely/",
"https://www.reddit.com/r/mentalhealth/comments/17hlsrs/i_feel_numb/",
"https://www.reddit.com/r/mentalhealth/comments/17hg5tj/feeling_uncomfortable_in_public/",


]

# Set up a SQLite database
conn = sqlite3.connect('reddit_data.db')
cursor = conn.cursor()

# Create a table to store the data
cursor.execute('''CREATE TABLE IF NOT EXISTS reddit_posts
                  (title TEXT, full_story TEXT, username TEXT, timestamp TEXT)''')

# Set up a Selenium webdriver
driver = webdriver.Chrome()  # You need to have Chrome and chromedriver installed

# Iterate through the list of URLs
for url in urls:
    # Extract the post ID from the URL
    post_id = urlparse(url).path.split('/')[4]
    button_id = f't3_{post_id}-read-more-button'

    # Navigate to the URL using Selenium
    driver.get(url)

    try:
        # Wait for the "Read more" button to appear and click it
        read_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, button_id))
        )
        read_more_button.click()
    except:
        print(f"Failed to click 'Read more' on {url}")

    # Wait for the full content to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, f't3_{post_id}-post-rtjson-content'))
    )

    # Get the HTML content of the page after clicking "Read more"
    page_content = driver.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Extract the title
    title_element = soup.find('h1', slot='title')

    if title_element:
        title = title_element.text.strip()
    else:
        title = "Title not found on {url}"

    # Extract and clean the story content and format it as a complete paragraph
    content = soup.find('div', class_='mb-sm mb-xs px-md xs:px-0')
    if content:
        paragraphs = content.find_all('p')
        story_text = '\n'.join(paragraph.get_text(strip=True) for paragraph in paragraphs)
    else:
        story_text = "Story content not found on {url}"

    # Extract the username
    username_element = soup.find('a', class_='author-name')
    if username_element:
        username = username_element.text.strip()
    else:
        username = "Username not found on {url}"

    # Print the extracted data
    print(f"Title for {url}: {title}")
    print("Story Content:")
    print(story_text)
    print(f"Username: {username}")

    #Extract Timestamp
    time_element = soup.find('time')
    time_stam = time_element['title']
    print("Date Time =", time_stam)

    # Modify the regular expression to make minutes part optional
    match = re.match(r'(\w+), (\w+ \d{1,2}, \d{4}) at (\d{1,2}:\d{2}:\d{2} [APM]+) (GMT[+-]\d{1,2}(:\d{2})?)', time_stam)

    if match:
        day, date, time, timezone_str, minutes_str = match.groups()
    
        # Set minutes to 0 if not provided
        minutes = int(minutes_str[1:]) if minutes_str else 0

        # Convert the extracted components to a datetime object
        formatted_date_time_str = f"{day}, {date} at {time}"
        datetime_obj = datetime.strptime(formatted_date_time_str, '%A, %B %d, %Y at %I:%M:%S %p')

        # Extract hours from the timezone string
        hours = int(re.search(r'[-+]\d{1,2}', timezone_str).group())

        # Calculate the timezone offset in minutes
        tz_offset = (hours * 60) + minutes

        # Apply the timezone offset
        timezone = pytz.FixedOffset(tz_offset)
        datetime_obj = datetime_obj.replace(tzinfo=timezone)

        print("Datetime object:", datetime_obj)
    else:
        print("Invalid date time format.")

    

    # Insert the data into the SQLite database
    cursor.execute("INSERT INTO reddit_posts (title, full_story, username, timestamp) VALUES (?, ?, ?, ?)", (title, story_text, username, datetime_obj))
    conn.commit()

# Close the SQLite database
conn.close()

# Close the Selenium webdriver
driver.quit()
