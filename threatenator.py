#!/usr/bin/env python3
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
"""
Fetch the current DEFCON level from the Australia government site
"""


LEVELS = {
    "error": 0,
    "certain": 1,
    "expected": 2,
    "probable": 3,
    "possible": 4,
    "notexpected": 5
}
NATIONAL_SECURITY_URL = "http://www.nationalsecurity.gov.au/"


def get_level():
    result = requests.get(NATIONAL_SECURITY_URL)
    soup = BeautifulSoup(result.content, features="html.parser")

    alert_level = soup.find("script", id="ThreatLevelJson")
    threat_data = json.loads(alert_level.string)

    return threat_data["ThreatLevelNo"]


def lambda_handler(event, context):
    """
    Return our status
    :param event:
    :param context:
    :return:
    """
    return {
        "statusCode": 200,
        "body": json.dumps({
            "data": {
                "type": "status",
                "id": "1",
                "attributes": {
                    "status": get_level()
                }
            }
        })
    }


if __name__ == "__main__":
    print(lambda_handler(None, None))
