import requests
import time
import os
from tqdm import tqdm
from datetime import datetime


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

def compare_and_update_files(new_file, old_file):
    new_lines = find_new_data(new_file, old_file)

    if new_lines:
        print("New data found:")
        for line in new_lines:
            print(line.strip())  

        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        new_data_file = f'url-list-{timestamp}.txt'
        with open(new_data_file, 'w', encoding='utf-8') as new_data_f:
            new_data_f.writelines(new_lines)
        print(f"New data written to {new_data_file}.")
    else:
        print("No new data added.")

    
    if os.path.exists(old_file):
        os.remove(old_file)
    os.rename(new_file, old_file)
    print(f"File saved as {old_file} for future comparison.")


def main():
    url = 'https://www.usom.gov.tr/url-list.txt'
    old_file = 'last-url-list.txt'  

    while True:
        
        new_file = 'last-url-list-temp.txt'
        
        
        download_file(url, new_file)

        
        compare_and_update_files(new_file, old_file)

        
        time.sleep(20)

if __name__ == "__main__":
    main()
