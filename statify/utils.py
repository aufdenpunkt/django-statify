# -*- coding: utf-8 -*-
#

# Core imports
import requests


def url_is_valid(url):
    valid_codes = [200, 301, 302]
    request = requests.get(url)

    if request.status_code in valid_codes:
        return True
    else:
        return False
