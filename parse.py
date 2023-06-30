import requests
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import os
import argparse

def parse_and_download(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml-xml')
    podcast_title = soup.find('title').text

    items = soup.find_all('item')
    items.reverse()

    # Use the podcast title to create directories for text and mp3 files if they do not exist
    text_dir = os.path.join(podcast_title, 'text_files')
    mp3_dir = os.path.join(podcast_title, 'mp3_files')
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(mp3_dir, exist_ok=True)

    def handle_item(i, item):
        title = item.find('title').text
        description = item.find('description').text

        # Write to text file
        filename_txt = os.path.join(text_dir, f"{str(i).zfill(3)}-{title}.txt")
        with open(filename_txt, 'w', encoding='utf-8') as f:
            f.write(description)

        # Download mp3 file
        enclosure = item.find('enclosure')
        if enclosure:
            mp3_url = enclosure.get('url')
            filename_mp3 = os.path.join(mp3_dir, f"{str(i).zfill(3)}-{title}.mp3")
            with requests.get(mp3_url, stream=True) as r:
                r.raise_for_status()
                with open(filename_mp3, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

    # Use a ThreadPoolExecutor to handle the items in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the handle_item function to the items list
        executor.map(handle_item, range(1, len(items) + 1), items)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse podcast XML feed and download MP3 files.')
    parser.add_argument('url', type=str, help='URL of the XML feed')
    args = parser.parse_args()
    
    parse_and_download(args.url)
