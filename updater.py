import requests
import json
import sys

response = requests.get('https://api.github.com/repos/NullSoldier/serverthrall/releases/latest')

if response.status_code != 200:
    print('Failed to update')
    sys.exit(1)

data = json.loads(response.content)

download_url = None

for asset in data['assets']:
    if asset['name'] == 'serverthrall.exe':
        download_url = asset['browser_download_url']
        break

if download_url is None:
    print('Cant find a serverthrall.exe in the latest released version')
    sys.exit(0)

print('Downloading ' + data['name'])
response = requests.get(download_url)

if response.status_code != 200:
    print('Failed to update')
    sys.exit(1)

try:
    with open('serverthrall.exe', 'wb') as file:
        file.write(response.content)
except PermissionError:
    print('Cant download to serverthrall.exe, close serverthrall first')
    sys.exit(1)
