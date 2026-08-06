import json
import os
import sys

sys.path.append(os.path.join(os.getcwd(), 'src'))
import generate_analysis
from bs4 import BeautifulSoup

# Simular request
req = {
    "asset": "BTCUSD",
    "type": "asset_full_report"
}
with open("bridge/antigravity_bridge_request.json", "w") as f:
    json.dump(req, f)

generate_analysis.main()

with open("bridge/antigravity_bridge_response.json", "r") as f:
    res = json.load(f)

html = res['ai_raw_text']
soup = BeautifulSoup(html, 'html.parser')
headers = soup.find_all('h3')
for i, h3 in enumerate(headers):
    if "4. Distribución" in h3.text:
        print(h3.find_next_sibling('p').text)
        print(h3.find_next_sibling('p').find_next_sibling('p').text)
        print(h3.find_next_sibling('p').find_next_sibling('p').find_next_sibling('p').text)
        print(h3.find_next_sibling('p').find_next_sibling('p').find_next_sibling('p').find_next_sibling('p').text)
        print(h3.find_next_sibling('p').find_next_sibling('p').find_next_sibling('p').find_next_sibling('p').find_next_sibling('p').text)

