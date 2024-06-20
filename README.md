
# Proxy Fetcher&Checker
Simple proxy parser/scraper and checker with multithreading proxy checking
## Features
- Fetch proxy from any proxy list
- Multithreaded proxy checking (4:03 to check 165k with 10000 threads on Ryzen 5 5600x)
- Proxies checked by several judges
- Configurable (currently trough editing config inside proxy_tester.py)
- Stable, with not drop because got wrong url/proxy

## Usage

Install the requirements
```sh
pip install -r requirements.txt
```

If you only need to fetch proxy, you can run proxy_fetcher.py
```sh
python proxy_fetcher.py
```
If you need checked proxy, run proxy_tester.py
> Note: Change `max_threads` inside proxy_tester.py to not choke your CPU
```sh
python proxy_tester.py
```
