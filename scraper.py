import os
import time
import requests
from bs4 import BeautifulSoup
import re

# Constants
BASE_URL = "https://medlineplus.gov/lab-tests/"
OUTPUT_DIR = "raw_tests"

# Folder bana lo agar nahi hai
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def sanitize_filename(name):
    """File name me se invalid characters hatane ke liye"""
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

def get_test_links():
    print(f"Fetching main list from {BASE_URL}...")
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    links = []
    # Saare alphabetic sections ke andar lists ko target karna
    ul_lists = soup.find_all('ul', class_='withident breaklist')
    for ul in ul_lists:
        for a_tag in ul.find_all('a'):
            links.append({
                'name': a_tag.text.strip(),
                'url': a_tag['href']
            })
    return links

def extract_and_save_test_data(test_info):
    test_name = test_info['name']
    test_url = test_info['url']
    
    try:
        response = requests.get(test_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Thoda robust heading search (in case MedlinePlus wording thodi change kare)
        target_heading = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'what do the results mean' in tag.text.lower())
        
        if not target_heading:
            print(f"[-] Skipping {test_name}: 'Results mean' section not found.")
            return

        content_blocks = []
        
        # Heading ke aage ka content nikalna jab tak agla H2 na aa jaye
        for sibling in target_heading.find_next_siblings():
            if sibling.name == 'h2':
                break
            content_blocks.append(sibling.text.strip())
            
        full_text = "\n".join(content_blocks)
        
        # Save to TXT
        filename = f"{sanitize_filename(test_name)}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Test Name: {test_name}\n")
            f.write(f"URL: {test_url}\n")
            f.write("--- CONTENT ---\n")
            f.write(full_text)
            
        print(f"[+] Saved: {filename}")
        time.sleep(1) # Be a good citizen, server block na kare isliye 1 sec delay
        
    except Exception as e:
        print(f"[!] Error processing {test_name}: {e}")

if __name__ == "__main__":
    test_links = get_test_links()
    print(f"Found {len(test_links)} tests. Starting extraction...")
    
    # Testing ke liye pehle sirf 5 test process kar raha hu. 
    # Jab code check kar le, toh [0:5] hata dena list se.
    for test in test_links: 
        extract_and_save_test_data(test)