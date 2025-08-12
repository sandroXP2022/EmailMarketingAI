import requests
import re
import csv
import time
import argparse
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.robotparser import RobotFileParser
from googlesearch import search

# Constants
REQUEST_DELAY = 2  # Delay between requests (in seconds)
MAX_RETRIES = 3    # Maximum number of retry attempts
robots_cache = {}  # Cache for robots.txt results

def check_robots_permission(url):
    """
    Check if scraping is allowed for the given URL using robots.txt
    """
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    if domain in robots_cache:
        return robots_cache[domain]
    
    robots_url = urljoin(domain, "/robots.txt")
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        allowed = rp.can_fetch("*", url)
    except:
        allowed = False
    
    robots_cache[domain] = allowed
    return allowed

def extract_emails_from_text(text):
    """
    Extract emails from text using regex
    """
    email_pattern = r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}'
    return list(set(re.findall(email_pattern, text)))

def email_filter(email):
    """
    Apply filtering rules to ignore unwanted emails
    """
    return (not email[0].isdigit() 
            and email.islower()
            and "-" not in email
            and "gdpr" not in email)

def get_domain_name(url):
    """
    Extract a readable domain name for site title fallback
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.split('.')
    if len(domain) > 1:
        return domain[-2].capitalize()
    return "Website"

def scrape_website(url):
    """
    Visit the website and extract valid emails
    """
    if not check_robots_permission(url):
        print(f"Access denied by robots.txt: {url}")
        return []
    
    headers = {"User-Agent": "Googlebot"}
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            retries += 1
            wait_time = REQUEST_DELAY * (2 ** (retries - 1))
            print(f"Error accessing {url}: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    else:
        print(f"Failed to access {url} after {MAX_RETRIES} attempts.")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string.strip() if soup.title else get_domain_name(url)
    emails = extract_emails_from_text(soup.get_text())
    time.sleep(REQUEST_DELAY)
    return [(email, url, title) for email in emails] if emails else []

def save_to_csv(data, filename="emails.csv"):
    """
    Save extracted emails to CSV file
    """
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for email, site, title in data:
            if email_filter(email):
                writer.writerow([email, site, title, datetime.now().strftime('%Y-%m-%d %H:%M:%S')])

def search_websites(limit=10, query=None):
    """
    Search for websites using Google and save results to websites.txt
    """
    if query is None:
        query = ""
    print(f"Searching for websites with query: {query}")
    
    results = []
    for url in search(query, num_results=limit):
        results.append(url)

    with open("websites.txt", "w") as f:
        for url in results:
            f.write(url + "\n")
    
    print(f"{len(results)} websites saved to websites.txt")

def extract_emails_from_file():
    """
    Extract emails from the websites listed in websites.txt
    """
    try:
        with open("websites.txt", "r") as f:
            websites = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("websites.txt not found. Run with --search first.")
        return
    
    scraped_emails = set()
    results = []
    
    for site in websites:
        print(f"Extracting contact info from: {site}")
        emails = scrape_website(site)
        for email, url, title in emails:
            if email not in scraped_emails:
                scraped_emails.add(email)
                results.append((email, url, title))
    
    if results:
        save_to_csv(results)
        print(f"{len(results)} emails saved to emails.csv")
    else:
        print("No emails found.")

def list_emails(filename="emails.csv"):
    """
    List all extracted emails from the CSV file
    """
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            print("Extracted emails:")
            for row in reader:
                print(row)
    except FileNotFoundError:
        print(f"{filename} not found.")

def main():
    parser = argparse.ArgumentParser(description="Email Collector for Contact Pages")
    parser.add_argument("--search", nargs="?", type=int, const=10, help="Search websites and save to websites.txt (optional: max number of results)")
    parser.add_argument("--query", type=str, help="Alternative search query for websites")
    parser.add_argument("--extract", action="store_true", help="Extract emails from websites saved in websites.txt")
    parser.add_argument("--list", action="store_true", help="List all extracted emails")
    
    args = parser.parse_args()
    
    if args.search is not None:
        search_websites(args.search, args.query)
    if args.extract:
        extract_emails_from_file()
    if args.list:
        list_emails()
    
    if args.search is None and not args.extract and not args.list:
        parser.print_help()

if __name__ == "__main__":
    main()

