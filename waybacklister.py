#!/usr/bin/env python3

import requests
import re
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import os
import tempfile
import random

# --- CONFIGURATION ---
MAX_RETRIES = 3
INITIAL_TIMEOUT = 15  # Increased initial timeout
RETRY_DELAY = 5       # Delay between retries
USER_AGENTS = [
    'WaybackLister/2.0',
    'Mozilla/5.0',
    'CustomBot/1.0 (+https://example.com/bot )',
]

def display_banner():
    banner = r"""
 __          __         _                _    _      _     _            
 \ \        / /        | |              | |  | |    (_)   | |           
  \ \  /\  / /_ _ _   _| |__   __ _  ___| | _| |     _ ___| |_ ___ _ __ 
   \ \/  \/ / _` | | | | '_ \ / _` |/ __| |/ / |    | / __| __/ _ \ '__|
    \  /\  / (_| | |_| | |_) | (_| | (__|   <| |____| \__ \ ||  __/ |   
     \/  \/ \__,_|\__, |_.__/ \__,_|\___|_|\_\______|_|___/\__\___|_|   
                   __/ |                                                
                  |___/                                                    
                                             
                   WaybackLister v1.1 by FR13ND0x7F
           Enhanced Directory Listing Detection Using Wayback Machine
    """
    print(banner)


def fetch_wayback_urls(domain):
    print(f"[+] Querying Wayback Machine for {domain}...")
    wayback_url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=txt&fl=original&collapse=urlkey"
    
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[*] Attempt {attempt} to fetch data for {domain}")
            with requests.get(wayback_url, stream=True, headers=headers, timeout=INITIAL_TIMEOUT) as response:
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8") as temp_file:
                    for line in response.iter_lines(decode_unicode=True):
                        if line.strip():
                            temp_file.write(line.strip() + "\n")
                    return temp_file.name
        except (requests.exceptions.RequestException, OSError) as e:
            print(f"[-] Error fetching data from Wayback Machine (Attempt {attempt}): {e}")
            if attempt < MAX_RETRIES:
                wait_time = RETRY_DELAY * attempt
                print(f"[*] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    return None


def extract_paths_for_domain(temp_file_path, target_domain):
    unique_paths = set()
    with open(temp_file_path, "r", encoding="utf-8") as temp_file:
        for line in temp_file:
            url = line.strip()
            parsed_url = urlparse(url)
            if parsed_url.hostname == target_domain:
                path = parsed_url.path.rstrip('/')
                if path and path != "/":
                    unique_paths.add(path)
    return sorted(unique_paths)


def extract_subdomains(temp_file_path, domain):
    subdomains = set()
    domain_parts = domain.split(".")
    domain_suffix = "." + ".".join(domain_parts[-2:])
    
    with open(temp_file_path, "r", encoding="utf-8") as temp_file:
        for line in temp_file:
            url = line.strip()
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            
            if hostname and hostname.endswith(domain_suffix) and hostname != domain:
                subdomains.add(hostname)
    
    return sorted(subdomains)


def check_directory_listing(domain, path):
    protocols = ["http", "https"]
    patterns = [
        "Index of /",
        "Directory Listing for",
        "<title>Index of",
        "Parent Directory</a>",
        "Last modified</a>",
        "Name</a>",
        "Size</a>",
        "Description</a>"
    ]
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    
    for protocol in protocols:
        url = f"{protocol}://{domain}{path}"
        try:
            response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
            if response.status_code == 200:
                for pattern in patterns:
                    if pattern in response.text:
                        return url
        except requests.exceptions.RequestException:
            continue
    return None


def process_domain(domain, paths, threads):
    print(f"[+] Processing domain: {domain}")
    
    if not paths:
        print(f"[-] No unique paths found for {domain}.")
        return
    
    print(f"[+] Found {len(paths)} unique paths for {domain}. Checking for directory listings...")
    
    directory_listings = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_directory_listing, domain, path) for path in paths]
        for future in as_completed(futures):
            result = future.result()
            if result:
                directory_listings.append(result)
                print(f"[+] Directory Listing Found: {result}")
    
    if directory_listings:
        print(f"\n[+] Summary of Directory Listings for {domain}:")
        for listing in directory_listings:
            print(f"  - {listing}")
    else:
        print(f"[-] No directory listings found for {domain}.")


def auto_discover_and_process(domain, threads):
    print(f"[+] Auto-discovering subdomains for {domain}...")
    temp_file_path = fetch_wayback_urls(domain)
    
    if not temp_file_path:
        print(f"[-] No archived URLs found for {domain}. Skipping.")
        return
    
    try:
        subdomains = extract_subdomains(temp_file_path, domain)
        domains_to_process = [domain] + subdomains
        
        print(f"[+] Found {len(domains_to_process)} targets to process:")
        for target in domains_to_process:
            print(f"  - {target}")
        
        for target_domain in domains_to_process:
            paths = extract_paths_for_domain(temp_file_path, target_domain)
            process_domain(target_domain, paths, threads)
    
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def process_domains_from_file(file_path, threads):
    try:
        with open(file_path, "r") as file:
            domains = [line.strip() for line in file if line.strip()]
        
        for domain in domains:
            if not re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain):
                print(f"[-] Invalid domain format for {domain}. Skipping.")
                continue
            
            print(f"\n[+] Processing domain from file: {domain}")
            temp_file_path = fetch_wayback_urls(domain)
            
            if temp_file_path:
                try:
                    paths = extract_paths_for_domain(temp_file_path, domain)
                    process_domain(domain, paths, threads)
                finally:
                    os.unlink(temp_file_path)
    
    except FileNotFoundError:
        print(f"[-] File not found: {file_path}")


def main():
    display_banner()
    parser = argparse.ArgumentParser(description="WaybackLister v2.0 - Enhanced Directory Listing Detection")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Single target domain to scan (e.g., example.com)")
    group.add_argument("-f", "--file", help="File containing a list of domains to scan (one per line)")
    group.add_argument("-auto", help="Automatically discover and scan subdomains for the given domain")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    args = parser.parse_args()

    if args.domain:
        if not re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", args.domain):
            print("[-] Invalid domain format. Please enter a valid domain.")
            return
        temp_file = fetch_wayback_urls(args.domain)
        if temp_file:
            try:
                paths = extract_paths_for_domain(temp_file, args.domain)
                process_domain(args.domain, paths, args.threads)
            finally:
                os.unlink(temp_file)
    
    elif args.file:
        process_domains_from_file(args.file, args.threads)
    
    elif args.auto:
        if not re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", args.auto):
            print("[-] Invalid domain format. Please enter a valid domain.")
            return
        auto_discover_and_process(args.auto, args.threads)


if __name__ == "__main__":
    main()
