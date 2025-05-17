import requests

proxy_ip = '127.0.0.1'
proxy_port = 63254

proxies = {
        'http': f'http://{proxy_ip}:{proxy_port}',
    }

r = requests.get(url="http://localhost:8765", proxies=proxies)


print(r.status_code)