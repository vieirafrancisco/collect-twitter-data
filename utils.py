import os
from typing import List

import pandas as pd
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

    return list(df["id"])


def read_input_file_with_screen_name(path: str) -> List[str]:
    df = pd.read_csv(path)

    if "screen_name" not in df.columns:
        return []

    return list(df["screen_name"])


def get_user_identifiers(file_path: str) -> List:
    identifiers = read_input_file_with_id(file_path)

    if identifiers == []:
        identifiers = read_input_file_with_screen_name(file_path)
        if identifiers == []:
            raise Exception("This file don't have id or screen_name columns!")

    return identifiers


def get_config() -> dict:
    with open("config.yaml", "r") as cf:
        config = yaml.load(cf, Loader=yaml.Loader)
    return config


def request_twitter_objects(
    file_path: str, user_arg=True, tline_arg=True, range=None
) -> None:
    api = get_twitter_api_instance()
    try:
        user_identifiers = get_user_identifiers(file_path)
    except Exception as e:
        raise Exception(e)

    config = get_config()

    for identifier in user_identifiers:
        if user_arg:
            try:
                user = api.get_user(identifier)
                save_user_object(user, config)
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)

        if tline_arg:
            try:
                timeline = api.user_timeline(identifier, count=200)
                save_user_timeline(timeline, config)
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)


def save_object(obj: object, path: str, file_name: str) -> None:
    file_path = path+file_name
    columns = list(obj._json.keys())
    instance = list(obj._json.values())

    if file_name not in os.listdir(path):
        df = pd.DataFrame([instance], columns=columns)
    else:
        df = pd.read_csv(file_path)
        new_instance_df = pd.DataFrame([instance], columns=columns)
        df = df.append(new_instance_df, ignore_index=True, sort=False)

    df.to_csv(file_path, index=False)


def save_user_object(user: object, config: dict) -> None:
    save_object(
        user,
        config["RESULTSET_PATH"], config["USER_TABLE"]
    )


def save_user_timeline(timeline: object, config: dict) -> None:
    for instance in timeline:
        save_object(
            instance,
            config["RESULTSET_PATH"], config["TIMELINE_TABLE"]
        )
