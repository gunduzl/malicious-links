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

def load_existing_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(line.strip() for line in file.readlines())
    return set()

def classify_data(lines):
    ipv4_pattern = re.compile(r'^\d{1,3}(\.\d{1,3}){3}$')
    ipv6_pattern = re.compile(r'^([0-9a-fA-F]{1,4}:){7}([0-9a-fA-F]{1,4})$')

    ips = set()
    domains = set()

    for line in lines:
        line = line.strip()
        if ipv4_pattern.match(line) or ipv6_pattern.match(line):
            ips.add(line)  
        else:
            domains.add(line)  

    return ips, domains

def update_files(new_ips, new_domains):
    
    existing_ips = load_existing_data('last-ips-list.txt')
    existing_domains = load_existing_data('last-domains-list.txt')

    # Find truly new IPs and domains
    new_unique_ips = new_ips - existing_ips
    new_unique_domains = new_domains - existing_domains

    # Append only new IPs and domains to last-ips-list.txt and last-domains-list.txt
    if new_unique_ips:
        with open('last-ips-list.txt', 'a', encoding='utf-8') as ip_file:
            ip_file.writelines(ip + '\n' for ip in new_unique_ips)

    if new_unique_domains:
        with open('last-domains-list.txt', 'a', encoding='utf-8') as domain_file:
            domain_file.writelines(domain + '\n' for domain in new_unique_domains)

    # Always overwrite new-detected-ips-domains-list.txt, and clear it if no new data
    with open('new-detected-ips-domains-list.txt', 'w', encoding='utf-8') as new_detected_file:
        if new_unique_ips or new_unique_domains:
            new_detected_file.writelines(ip + '\n' for ip in new_unique_ips)
            new_detected_file.writelines(domain + '\n' for domain in new_unique_domains)
        else:
            new_detected_file.write('')  # Empty the file if no new data

    # Append all new data (IPs + Domains) to total-malicious-list.txt
    all_new_data = new_ips.union(new_domains)
    existing_total = load_existing_data('total-malicious-list.txt')
    new_total_data = all_new_data - existing_total

    if new_total_data:
        with open('total-malicious-list.txt', 'a', encoding='utf-8') as total_file:
            total_file.writelines(data + '\n' for data in new_total_data)

    return new_unique_ips, new_unique_domains

def process_file(new_file):
    # Read the new file and classify its contents into IPs and domains
    new_lines = set(open(new_file, 'r', encoding='utf-8').readlines())
    new_ips, new_domains = classify_data(new_lines)

    # Update all related files
    return update_files(new_ips, new_domains)

def main():
    url = 'https://www.usom.gov.tr/url-list.txt'

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_file = f'total-malicious-list-{timestamp}.txt'

        # Download the file
        download_file(url, new_file)

        # Process the new file and update other files
        new_ips, new_domains = process_file(new_file)

        # Delete the temporary file after processing
        if os.path.exists(new_file):
            os.remove(new_file)
            print(f"Temporary file {new_file} deleted.")

        print(f"Iteration completed. New IPs: {len(new_ips)}, New Domains: {len(new_domains)}")

        # Wait for the next iteration
        time.sleep(180)

if __name__ == "__main__":
    main()
