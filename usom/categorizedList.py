import requests
import time
import os
from tqdm import tqdm
from datetime import datetime
import re

def download_file(url, file_name):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(file_name, 'wb') as file:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading", ascii=True) as progress_bar:
            for chunk in response.iter_content(1024):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
    print(f"File {file_name} downloaded.")

def find_new_data(new_file, old_file):
    if not os.path.exists(old_file):
        return []

    with open(new_file, 'r', encoding='utf-8') as file1, open(old_file, 'r', encoding='utf-8') as file2:
        new_data = set(file1.readlines())
        old_data = set(file2.readlines())

    new_lines = list(new_data - old_data)
    return new_lines

def classify_data(lines):
    # Regex patterns for IPv4, IPv6, and complex domain validation
    ipv4_pattern = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')
    ipv6_pattern = re.compile(r'^([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4})$')
    # Complex domain regex
    domain_pattern = re.compile(r'^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$')

    ips = []
    domains = []
    urls = []

    for line in lines:
        line = line.strip()
        if ipv4_pattern.match(line) or ipv6_pattern.match(line):
            ips.append(line)
        elif domain_pattern.match(line):
            domains.append(line)  # Domains that match the complex regex
        else:
            urls.append(line)  # Anything else will be considered a URL

    return ips, domains, urls

def compare_and_update_files(new_file):
    ips, domains, urls = classify_data(open(new_file, 'r', encoding='utf-8').readlines())

    with open('last-ips.txt', 'a', encoding='utf-8') as ip_f:  # Open in append mode
        ip_f.writelines(ip + '\n' for ip in ips)

    with open('last-domains.txt', 'a', encoding='utf-8') as domain_f:  # Open in append mode
        domain_f.writelines(domain + '\n' for domain in domains)

    with open('last-urls.txt', 'a', encoding='utf-8') as url_f:  # Open in append mode
        url_f.writelines(url + '\n' for url in urls)
    
    print("Data appended to 'last-ips.txt', 'last-domains.txt', and 'last-urls.txt'.")

def main():
    url = 'https://www.usom.gov.tr/url-list.txt'
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_file = f'total-malicious-list-{timestamp}.txt'
        
        download_file(url, new_file)

        compare_and_update_files(new_file)

        time.sleep(20)

if __name__ == "__main__":
    main()
