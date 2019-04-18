import time
import os
from typing import List

import pandas as pd
import tweepy
import yaml
import json


def get_twitter_api_instance():
    with open("config.key.yaml", "r") as f:
        credentials_file = yaml.load(f, Loader=yaml.Loader)

    auth = tweepy.OAuthHandler(
        credentials_file["CONSUMER_KEY"],
        credentials_file["CONSUMER_SECRET"])

    auth.set_access_token(
        credentials_file["ACCESS_TOKEN"],
        credentials_file["ACCESS_TOKEN_SECRET"]
    )

    api = tweepy.API(
        auth,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True
    )

    if(not api):
        raise Exception("Can't instantiate the twitter api")

    return api


def get_users_identifiers(file_path: str) -> List[int]:
    df = pd.read_csv(file_path)

    if 'id' in df.columns:
        identifiers = list(df['id'])
    else:
        raise Exception("This file don't have id column!")

    return identifiers


def get_config() -> dict:
    with open("config.yaml", "r") as cf:
        config = yaml.load(cf, Loader=yaml.Loader)
    return config


def filter_identifiers(
    identifiers: List[int], config: dict, irange: List[int]
) -> List[int]:
    temp_identifiers = identifiers

    if irange:
        temp_identifiers = temp_identifiers[irange[0]:irange[1]]

    if config["TIMELINE_TABLE"] in os.listdir(config["RESULTSET_PATH"]):
        curr_identifiers = pd.read_csv(config["COMPLETE_TLINE_PATH"]).values
        temp_identifiers = [
            identifier
            for identifier in temp_identifiers
            if identifier not in curr_identifiers]

    return temp_identifiers


def request_twitter_objects(
    file_path: str, user_arg=True, tline_arg=True, irange=None
) -> None:
    api = get_twitter_api_instance()
    config = get_config()

    try:
        user_identifiers = get_users_identifiers(file_path)
    except Exception as e:
        raise Exception(e)

    user_identifiers = filter_identifiers(user_identifiers, config, irange)

    for identifier in user_identifiers:
        if user_arg:
            try:
                begin = time.time()
                user = api.get_user(identifier)
                save_user_object(user, config)
                end = time.time()
                print("User {} object, success! => {:.2f}s".format(
                    identifier, end-begin))
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)

        if tline_arg:
            try:
                begin = time.time()
                timeline = api.user_timeline(identifier, count=200)
                save_user_timeline(identifier, timeline, config)
                end = time.time()
                print("User {} timeline, success! => {:.2f}s".format(
                    identifier, end-begin))
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)


def save_dataframe(df: object, path: str, file_name: str) -> None:
    file_path = path+file_name

    if file_name in os.listdir(path):
        curr_df = pd.read_csv(file_path)
        curr_df = curr_df.append(df, ignore_index=True, sort=False)
        curr_df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, index=False)


def save_user_object(user: object, config: dict) -> None:
    df = pd.DataFrame(
        [json.dumps(user._json, ensure_ascii=False)], columns=["user_object"])

    save_dataframe(
        df,
        config["RESULTSET_PATH"], config["USER_TABLE"]
    )


def save_user_timeline(
    identifier: int, timeline: object, config: dict
) -> None:
    objects = [
        [identifier, json.dumps(instance._json, ensure_ascii=False)]
        for instance in timeline]
    df = pd.DataFrame(objects, columns=["id", "status_object"])

    save_dataframe(
        df,
        config["RESULTSET_PATH"], config["TIMELINE_TABLE"]
    )
