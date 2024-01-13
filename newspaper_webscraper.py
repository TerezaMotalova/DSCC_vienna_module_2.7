"""A SIMPLE PROTOTYPE FOR WEB-SCRAPING OF NEWSPAPER ARTICLES"""

# SOURCES
# 1) Documentation for the datetime library: https://docs.python.org/3/library/datetime.html#module-datetime
# 2) Documentation for the json library: https://docs.python.org/3/library/json.html#module-json
# 3) Documentation for the os library, path module: https://docs.python.org/3/library/os.path.html#module-os.path
# 4) Documentation for the BeautifulSoup library: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#
# 5) Documentation for the requests library: https://requests.readthedocs.io/en/latest/user/quickstart/
# 6) Guide on how to parse webpage data: https://www.learndatasci.com/tutorials/ultimate-guide-web-scraping-w-python-requests-and-beautifulsoup/
# 7) Guide on how to generate random code: https://www.geeksforgeeks.org/python-generate-random-string-of-given-length/"""

# README: How to use the script
# 1) Create a main folder where all files will be stored,
# 2) Save "newspaper_webscraper.py" in the main folder,
# 3) Inside the main folder, create a sub-folder where original/raw URL content in html format will be stored, e.g. "newspaper_raw_data",
# 4) Inside the main folder, create a .txt file where metadata and research data will be stored, e.g. newspapers_metadata.txt,
# 5) Create the same header line in the .txt file as in newspapers_metadata.txt,
# 6) Run the script,
# 7) Check outcomes.

# CODE

# import of needed libraries:
## os, random, string, datetime (buil-in libraries)
## requests and BeautifulSoup (must be installed, e.g. using pip command)

from datetime import datetime
import json
import os
from random import choices
from string import ascii_uppercase, digits

from bs4 import BeautifulSoup
import requests


def get_data_from_URL(user_URL):
    """gets html data from a given URL and checks whether the request was successful"""

    URL_data = requests.get(user_URL)
    # if status code == 200, i.e. the request has been successful, the condition is true and this branch is executed
    if URL_data.status_code == requests.codes.ok: 
        return URL_data
    # else branch not needed, if 1st condition is true, the function ends before the next line is executed
    return "request failed"


def get_directory():
    """recursively asks user to provide a correct folder/file directory, or abort this operation"""

    user_directory = input("Give me a correct - absolute/relative - path where I can store the data, or abort this by typing END: ")
    check = os.path.exists(user_directory)
    if check == True or user_directory == "END":
        return user_directory
    return get_directory()


def check_output(html_retrieved_data):
    """checks if it is possible to retrieve a required item from the parsed html data,
       if not, it replaces the None value with a string "NA", i.e. Not Available"""

    if html_retrieved_data == None:
        return "NA"
    return html_retrieved_data


def get_data_from_html(parsed_html):
    """gets required items from parsed html data while looking for specific tags"""

    # get publisher
    publisher = check_output(parsed_html.find(attrs={"name": "publisher"})) 
    if publisher != "NA":
        publisher = publisher.get("content")

    # get author(s)
    author = check_output(parsed_html.find(attrs={"name": "author"}))
    if author != "NA":
        author = author.get("content")

    # get publication date
    pub_date = check_output(parsed_html.find(attrs={"name": "datePublished"}))
    if pub_date != "NA":
        pub_date = pub_date.get("content")

    # get title
    title = check_output(parsed_html.find("title"))
    if title != "NA":
        title = title.get_text()

    # get description
    description = check_output(parsed_html.find(attrs={"name": "description"}))
    if description != "NA":
        description = description.get("content")

    return publisher, author, pub_date, title, description

    
def get_data_from_json(retrived_json):
    """gets required items from JSON-LD data while looking for specific keys"""

    retrived_json = retrived_json.get_text()
    retrived_json = json.loads(retrived_json)

    if type(retrived_json) == list:
        retrived_json = retrived_json[0]

    # get publisher
    publisher = retrived_json.get("publisher", "NA")
    if publisher != "NA":
        publisher = publisher.get("name", "NA")

    # get author(s)
    author = retrived_json.get("author", "NA")
    if type(author) == dict:
        author = author.get("name", "NA")
    elif type(author) == list:
        author = [item.get("name", "NA") for item in author]

    # get publication date
    pub_date = retrived_json.get("datePublished", "NA")

    # get title
    title = retrived_json.get("headline", "NA")

    # get description
    description = retrived_json.get("description", "NA")

    return publisher, author, pub_date, title, description


def parse_data(user_URL_content):
    """parses html data by using BeautifulSoup library and gather metadata and research data"""

    parsed_html = BeautifulSoup(user_URL_content, "html.parser")

    retrived_json = check_output(parsed_html.find(attrs={"type": "application/ld+json"}))
    if retrived_json != "NA":
        publisher, author, pub_date, title, description = get_data_from_json(retrived_json)
    else:
        publisher, author, pub_date, title, description = get_data_from_html(parsed_html)

    # get text based on <p></p> tags; however, this omits <h2></h2> headers and higher, and it is not 100 % cleaned
    text = check_output(parsed_html.find_all("p"))
    if text != "NA":
        text = " ".join([item.get_text().strip() for item in text])

    return publisher, author, pub_date, title, description, text


def main():
    """manages the procedure and calls other functions"""

    # asking user for URL to be scraped
    user_URL = input("Dear, what should I scrape for you? Start the URL with https://: ")

    # checking whether URL is correct (simplified)
    if not user_URL.startswith("https://"):
        print("I told you to use https://! Run me again and give me the correct URL!")
        return  # terminates the script

    # sending a request to URL
    URL_content = get_data_from_URL(user_URL.strip())

    # evaluating the request's result
    if URL_content == "request failed":
        print("My apologies, I cannot access the URL content.")
        return  # terminates the script
    print("We got the data!")

    # asking user for a directory where to store original/raw URL content in html format  
    raw_data_dir = get_directory()
    if raw_data_dir == "END":
        print("Done here!")
        return  # terminates the script

    # checking the current day and time to store URL content chronologically
    current_datetime = datetime.now().strftime("%y-%m-%d_%H-%M-%S")

    # creating ID for URL content, code snippet used from: https://www.geeksforgeeks.org/python-generate-random-string-of-given-length/
    URL_content_ID = "".join(choices(ascii_uppercase + digits, k=9))

    # creating path for a file where URL content will be saved
    URL_content_path = os.path.join(raw_data_dir, f"{current_datetime}_{URL_content_ID}_newspaper_article.html")
    URL_content_abs_path = os.path.abspath(URL_content_path)
    
    # saving the file containing URL content in the directory
    with open(URL_content_path, mode="w", encoding="utf-8") as raw_file:
        print(BeautifulSoup(URL_content.content, "html.parser").prettify(), file=raw_file)
    print("Raw html data from the URL saved!")

    # asking user for a file directory where to add new metadata and research data
    parsed_file_dir = get_directory()
    if parsed_file_dir == "END":
        print("Done here!")
        return  # terminates the script
    
    # parsing URL content
    publisher, author, pub_date, title, description, text = parse_data(URL_content.content)

    # asking user for keywords for new metadata and research data
    user_keywords = input("Which keywords should I store for this article, hm? (Use comma to separate them, e.g. banana, mango, pineapple): ")
    cleaned_keywords = [word.strip() for word in user_keywords.split(",")]

    # saving new metadata and research data to the file
    data_to_be_saved = [URL_content_ID, publisher, author, pub_date, title, description, text, user_URL, current_datetime, cleaned_keywords, URL_content_abs_path]
    with open(parsed_file_dir, mode="a", encoding="utf-8") as raw_file:
        for data_item in data_to_be_saved:
            print(data_item, file=raw_file, end="\t")
        print(file=raw_file)  # preparing for next appending on a new line
    print("Scraped html data saved! Bye!")

    return


main()
