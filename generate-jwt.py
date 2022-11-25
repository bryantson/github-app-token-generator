#!/usr/bin/env python3

import sys
import jwt
import time
import os
import requests

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend

current_time = int(time.time())

app_id = sys.argv[1]
organization = sys.argv[2]

payload = {
    # issued at time
    'iat': current_time,

    # JWT expiration time (10 minute maximum)
    'exp': current_time + (10 * 60),

    # GitHub App's identifier – you can get it from the github application dashboard
    'iss': app_id,
}

private_key_file_content = sys.argv[3]

if private_key_file_content is not None:
    private_key_file_content=private_key_file_content.encode()

    cert_obj = load_pem_private_key(private_key_file_content, password=None, backend=default_backend())
    app_jwt = jwt.encode(payload, private_key_file_content, algorithm='RS256')

    headers_app_installations = {
        "Authorization": "Bearer " + app_jwt,
        "Accept": "application/vnd.github+json"
    }

    response_app_installations = requests.request("GET","https://api.github.com/app/installations", headers=headers_app_installations)

    for app_installation in response_app_installations.json():
        
        if(app_installation['account']['login'] == organization):
            app_installation_id = app_installation['id']

        headers_app_token = {
            "Authorization": "Bearer " + app_jwt,
            "Accept": "application/vnd.github+json"
        }

        resp_token = requests.request("POST","https://api.github.com/app/installations/" + str(app_installation_id) + "/access_tokens", headers=headers_app_token)
        encoded_app_token = resp_token.json()['token']

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
      print(f'token={encoded_app_token}', file=fh)
