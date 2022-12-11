import requests
import os
import json
import sys
from primitive_objects import TwitterData
import json
import pandas as pd
from primitive_objects import Authors, SemSchPaper
import numpy as np
from tqdm import tqdm
import json
import re
sys.path.append("../data/")
from twitter_key import TwitterCreds

bearer_token = TwitterCreds.BEARER_TOKEN

def create_url():
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values. _akhaliq,ducha_aiki
    usernames = "usernames=twitterdev,twitterapi,_akhaliq"
    user_fields = "user.fields=id,protected"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()



def main():
    url = create_url()
    json_response = connect_to_endpoint(url)
    data = json.dumps(json_response, indent=4, sort_keys=True)

    


if __name__ == "__main__":
    main()