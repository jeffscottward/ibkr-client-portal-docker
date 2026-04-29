#!/usr/bin/env python3
"""Blog-post baseline example: fetch AAPL contract metadata after gateway login."""

from __future__ import annotations

import json

import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

contract_id = 265598
url = f"https://localhost:5000/v1/api/iserver/contract/{contract_id}/info"

session = requests.Session()
session.verify = False

response = session.get(url, timeout=15)
response.raise_for_status()

print(json.dumps(response.json(), indent=2, sort_keys=True))
