import requests
import re

def parse_FreeproxyWorld(url):
    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            html_content = response.content.decode('utf-8')

            ip_pattern = re.compile(r'<td class="show-ip-div">\n(\d+\.\d+\.\d+\.\d+)')
            port_pattern = re.compile(r'<a href="/\?port=(\d+)">')
            type_patter = re.compile(r'<a href="/\?type=(http|https|socks4|socks5)">')

            ips = ip_pattern.findall(html_content)
            ports = port_pattern.findall(html_content)
            types = type_patter.findall(html_content)
            ip_ports = [f"{type}://{ip}:{port}" for type, ip, port in zip(types, ips, ports)]
            return ip_ports
        else:
            return None
    except Exception as e:
        print(f"Failed to fetch proxy from {url}. Got: {e}")