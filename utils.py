from typing import List

import pandas as pd
import numpy as np
import tweepy
import yaml


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
        print("Something wrong!")
        return 0

    return api


def read_input_file_with_id(path: str) -> List[int]:
    df = pd.read_csv(path)

    if "id" not in df.columns:
        return []

    return df["id"]


def read_input_file_with_screen_name(path: str) -> List[str]:
    df = pd.read_csv(path)

    if "screen_name" not in df.columns:
        return []

    return df["screen_name"]


def get_user_identifiers(file_path: str) -> List:
    identifiers = read_input_file_with_id(file_path)

    if identifiers == []:
        identifiers = read_input_file_with_screen_name(file_path)
        if identifiers == []:
            raise Exception("This file don't have id or screen_name columns!")

    return identifiers


def request_twitter_objects(
    file_path: str, user_arg=True, tline_arg=True, range=None
) -> None:
    api = get_twitter_api_instance()
    user_identifiers = get_user_identifiers(file_path)

    if user_arg:
        for identifier in user_identifiers:
            try:
                user = api.get_user(identifier)
                save_user_object(user)
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)

    if tline_arg:
        for identifier in user_identifiers:
            try:
                timeline = api.user_timeline(identifier)
                save_user_object(timeline)
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)


def save_user_object(user: object) -> None:
    pass


def save_user_timeline(timeline: object) -> None:
    pass
