import requests
import os
import re
from utils.freeproxy_world_parser import parse_FreeproxyWorld


proxies = set()

def fetch_proxies(url):
    url_got = url
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            try:
                if response.text[0] == "{":
                    data = response.json()
                    fetch_proxies_json(data)
                elif "freeproxy.world" in url:
                    proxy_list = parse_FreeproxyWorld(url)
                    if proxy_list:
                        for proxy in proxy_list:
                            protocol, rest = proxy.split("://")
                            ip, port = rest.split(":")
                            add_to_list(protocol, ip, port)
                else:
                    fetch_list(response.text.splitlines(), url_got)
                    
            except Exception as e:
                print(f"Error processing response from {url}: {e}")
        else:
            print(f"Failed to fetch proxies from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to fetch proxies from {url}: {e}")

def add_to_list(protocol, ip, port):
    proxies.add(f"{protocol}://{ip}:{port}")

def fetch_proxies_json(data):
    for proxy in data['data']:
        protocol = proxy['protocols'][0]
        ip = proxy['ip']
        port = proxy['port']
        add_to_list(protocol, ip, port)

def fetch_list(data, url):
    for proxy in data:
        if is_valid_proxy(proxy):
            if "://" in proxy:
                protocol, address = proxy.split("://")
                ip, port = address.split(":")
                add_to_list(protocol, ip, port)
            else:
                stripped_url = url.replace("https://", "")
                protocol =  determine_protocol(stripped_url)
                ip, port = proxy.split(":")
                add_to_list(protocol, ip, port)

def is_valid_proxy(proxy):
    regex = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')
    return bool(regex.match(proxy))

def determine_protocol(url):
    if "socks5" in url:
        return "socks5"
    elif "socks4" in url:
        return "socks4"
    elif "https" in url:
        return "https"
    elif "http" in url:
        return "http"
    else:
        print(f"Not sure about proxy protocol at {url}")
        return "http"

def add_proxies_to_file():
    with open('proxies.txt', 'a') as file:
        for proxy in proxies:
            file.write(proxy + '\n')

def fetchProxy():
    if os.path.exists("proxies.txt"):
        print("Found proxies.txt // Deleting...")
        os.remove("proxies.txt")
    with open("urlToParse.txt", 'r') as file:
        proxy_urls= [line.strip() for line in file]
    for proxy_url in proxy_urls:
        print(f"Fetching from: {proxy_url}")
        fetch_proxies(proxy_url)
    
    # Write all unique proxies to the file after processing all URLs
    add_proxies_to_file()

if __name__ == "__main__":
    fetchProxy()