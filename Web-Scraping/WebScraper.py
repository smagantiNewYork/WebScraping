import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def textCleaning():
    lines_seen = set()
    outfile = open('NoDuplicates.txt','w')
    for line in open("NotHR.txt", "r"):
        if line not in lines_seen: # not a duplicate
            outfile.write(line)
            lines_seen.add(line)
    outfile.close()
    

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    response = requests.get(url)
    filename = os.path.join(dest_folder, os.path.basename(urlparse(url).path))
    with open(filename, 'wb') as file:
        file.write(response.content)
    # print(f"Downloaded: {filename}")
    
visited_urls = set()

def traverse_and_download(url, base_url, dest_folder):

    global visited_urls

    # This avoids revisting the same links to improve runtime
    if url in visited_urls: 
        return
    else:
        visited_urls.add(url)

    # This makes sure that if any url causes access problems or is broken, returns a broken status code like 404 for example
    try:
        response = requests.get(url)
        if response.status_code == 200:
            pass
        else:
            print("Did not work with status code: {}".format(response.status_code))
            return

    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request:", e)
        return


    soup = BeautifulSoup(response.content, 'html.parser')
    # This finds all the hyperlinks on a website
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if not href:
            continue
        # full_url = urljoin(url, href)
        full_url = href
        # print(full_url)
        parsed_url = urlparse(full_url)

        if full_url.endswith(('.pdf', '.docx')) or 'wp-content' in full_url:
            download_file(full_url, dest_folder)
            print("{} - Downloaded to {}".format(full_url, dest_folder))
        else:
            print("{} - Skipped".format(full_url))
            file = open('NotHR.txt','a')
            # file.write("{}){}\n".format(i, url))
            file.write("{}\n".format(url))

        # Issue is that the website changes like human resources switches to payroll!
        if parsed_url.path.startswith(urlparse(base_url).path) and parsed_url.path != urlparse(url).path:
            sub_folder = dest_folder + parsed_url.path
            # print(sub_folder)
            traverse_and_download(full_url, sub_folder, sub_folder)

        # Trying to figure out how to scrape only if it is redirected from hr but issue is that it will scrape the entire Cohen & Steers Website.
        # elif "cnscentral.cohenandsteers.com" in full_url:
        #     last_part = base_url.rstrip('/').split('/')[-1]
        #     # print(last_part)
        #     # destination_folder = "H:\Web-Scraping\ScrapedData\{}".format(last_part)
        #     traverse_and_download(full_url, dest_folder + last_part, dest_folder + last_part)


if __name__ == "__main__":
    start = time.time()
    base_url = "https://cnscentral.cohenandsteers.com/human-resources/"
    last_part = base_url.rstrip('/').split('/')[-1]
    destination_folder = "H:\Web-Scraping\ScrapedData\{}".format(last_part)
    # destination_folder = "H:\Web-Scraping\ScrapedData"
    traverse_and_download(base_url, base_url, destination_folder)
    textCleaning()
    end = time.time()
    totalTime = end - start
    print(totalTime)
