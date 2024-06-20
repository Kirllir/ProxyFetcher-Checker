import pycurl
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import random
import os
from proxy_fetcher import fetchProxy
from collections import deque

fetchProxy()

# Proxy Judges
judges = [ 
    "http://httpheader.net/azenv.php",
    "http://azenv.net/",
    "http://proxyjudge.us/",
    "https://wfuchs.de/azenv.php",
    "https://aranguren.org/azenv.php",
    "http://www3.wind.ne.jp/hassii/env.cgi",
    "https://www2t.biglobe.ne.jp/~take52/test/env.cgi"
]

timeout = 5 # In seconds how long to wait before dropping connection
retries = 2 # How many retries to do if fails
max_threads = 10000 # Threads to run concurrently
input_file = 'proxies.txt' # Name of input file
output_file = 'tested.txt' # Name of output file
cycle = 2 # Itterations of checks. Test proxies from file -> get working -> test them -> and so on "cycle" amount of times
judgesAmount = 4 # Amount of judges to run check proxy with. More judges = longer checks = better results. Note: 50%+ of judges give positive = proxy considered working

# Test proxy using curl
def test_proxy(proxy, working_judges, timeout=timeout, retries=retries):
    results = []
    for judge in working_judges:
        buffer = BytesIO()
        curl = pycurl.Curl()
        protocol = proxy.split('://')[0]
        curl.setopt(pycurl.URL, judge)
        curl.setopt(pycurl.TIMEOUT, timeout)
        #curl.setopt(pycurl.ACCEPT_ENCODING, "gzip, deflate")
        curl.setopt(pycurl.ACCEPT_ENCODING, "")

        if protocol in ['http', 'https']:
            curl.setopt(pycurl.PROXY, proxy.split('://')[1])
            curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
            if protocol == 'https':
                curl.setopt(pycurl.SSL_VERIFYPEER, 0)
                curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        elif protocol == 'socks4':
            curl.setopt(pycurl.PROXY, proxy.split('://')[1])
            curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
        elif protocol == 'socks5':
            curl.setopt(pycurl.PROXY, proxy.split('://')[1])
            curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        else:
            curl.setopt(pycurl.PROXY, proxy)
            curl.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_HTTP)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        

        try:
            start_time = time.time()
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            end_time = time.time()
            latency = end_time - start_time
            curl.close()

            if status_code == 200:
                response = buffer.getvalue().decode('utf-8')
                http_host_line = f"HTTP_HOST = {judge.split('://')[1].split('/')[0]}"
                if http_host_line in response:
                    #print(response)
                    results.append(latency * 1000)
        except pycurl.error:
            continue
        finally:
            buffer.close()

    success_latencies = [latency for latency in results if latency is not None]
    if len(success_latencies) >= len(working_judges) / 2:
        average_latency = sum(success_latencies) / len(success_latencies)
        return {
            "proxy": proxy,
            "average_latency": average_latency
        }
    return None

# Reading proxies from file
def read_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file]
    return proxies

# Writing proxies to file
def write_proxies(file_path, proxies):
    with open(file_path, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy['proxy']} {proxy['average_latency']:.2f}ms\n")

# Judge test
def test_judge(judge):
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, judge)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    curl.setopt(pycurl.TIMEOUT, timeout)
    
    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()
        if status_code == 200:
            return True
    except pycurl.error:
        return False
    finally:
        buffer.close()
    return False

def main():
    global working_judges
    working_judges = [judge for judge in judges if test_judge(judge)]
    if not working_judges:
        print("No working judges available.")
        return

    print(f"Working judges: {working_judges}")

    if len(working_judges) > judgesAmount:
        working_judges = random.sample(working_judges, judgesAmount)
    print(f"Selected judges: {working_judges}")

    proxies = read_proxies(input_file)
    proxies_deque = deque(proxies)

    for _ in range(cycle):
        working_proxies = []
        with ThreadPoolExecutor(max_threads) as executor:
            future_to_proxy = {executor.submit(test_proxy, proxy, working_judges): proxy for proxy in proxies_deque}
            with tqdm(total=len(future_to_proxy)) as pbar:
                for future in as_completed(future_to_proxy):
                    try:
                        result = future.result()
                        if result:
                            working_proxies.append(result)
                            #print(f'Working: {result}')
                    except Exception as e:
                        print(f"Unexpected error with proxy {future_to_proxy[future]}: {e}")
                    finally:
                        pbar.update(1)

        proxies_deque = deque([proxy['proxy'] for proxy in working_proxies])

    if os.path.exists(output_file):
        print(f"Found {output_file} // Deleting...")
        os.remove(output_file)
    write_proxies(output_file, working_proxies)

if __name__ == '__main__':
    main()