from bs4 import BeautifulSoup
import requests

response1 = requests.get("https://www.freshersworld.com/jobs?src=homeheader")
page = response1.text

# Parse the HTML content
soup = BeautifulSoup(page, "html.parser")

# Find all span elements with class "wrap-title seo_title"
tag = soup.find_all(name="span", class_="wrap-title seo_title")

# Initialize lists to store the scraped data
texts = []
links = []

# Extract the text and links
for a in tag:
    text = a.getText()
    texts.append(text)

# Print the scraped data
print(texts)

