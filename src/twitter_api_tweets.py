import requests
import os
import json
import sys
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
    # Replace with user ID below
    user_id = 2465283662
    return "https://api.twitter.com/2/users/{}/tweets".format(user_id)


def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {"tweet.fields": "public_metrics", "max_results":100, "start_time":"2019-01-01T17:00:00Z"}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
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
    params = get_params()
    json_response = connect_to_endpoint(url, params)

    # with open("../data/all_authors.txt", 'r') as f:
    #     author_ids = f.readlines()
    # with open("../data/all_papers.txt", 'r') as f:
    #     paper_ids = f.readlines()
    # author_ids = [f.replace("\n","") for f in author_ids]
    # paper_ids = [f.replace("\n","") for f in paper_ids]

    # with open("../data/papers.json", 'r') as f:
    #     cache_papers = json.load(f)

    # with open("../data/authors.json", 'r') as f:
    #     cache_authors = json.load(f)
    data = json_response["data"]
    tweets = []
    for i, d in enumerate(data):
        # print(d)
        public_metrics = d["public_metrics"]
        tweet = TwitterData(i, 
        d["text"], 
        public_metrics["retweet_count"],
        public_metrics["reply_count"],
        public_metrics["like_count"],
        public_metrics["quote_count"]
        )
        tweets.append(tweet)
    twitter_dict = {}
    for tweet in tweets:
        local_dict = {}
        local_dict["paper_id"] = tweet.paper_id
        local_dict["text"] = tweet.text
        local_dict["retweet_count"] = tweet.retweet_count
        local_dict["reply_count"] = tweet.reply_count
        local_dict["like_count"] = tweet.like_count
        local_dict["quote_count"] = tweet.quote_count
        twitter_dict[tweet.paper_id] = local_dict
    with open("../data/twitter_papers.json","w") as f:
        json.dump(twitter_dict, f)



if __name__ == "__main__":
    main()