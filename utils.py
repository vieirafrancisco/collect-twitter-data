import time
import os
import re
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


def get_config(infile_name: str) -> dict:
    with open("config.yaml", "r") as cf:
        config = yaml.load(cf, Loader=yaml.Loader)

    config["USER_TABLE"] = config["USER_TABLE"].format(infile_name)

    pattern = re.compile(
        config["TIMELINE_TABLE"].format(infile_name, "(\\d+)"))
    cont = len([f for f in os.listdir(config["TIMELINE_PATH"])
                if pattern.match(f)]) + 1

    config["TIMELINE_TABLE"] = config["TIMELINE_TABLE"].format(
        infile_name,
        cont
    )

    return config


def filter_identifiers(
    identifiers: List[int], config: dict, irange=None
) -> List[int]:
    temp_identifiers = identifiers
    user_file_name = config["USER_TABLE"]
    user_path = config["USER_PATH"]

    if irange:
        temp_identifiers = temp_identifiers[irange[0]:irange[1]]

    if user_file_name in os.listdir(user_path):
        curr_identifiers = [
            json.loads(instance)["id"]
            for instance in pd.read_csv(
                user_path + user_file_name)["user_object"].values]
        temp_identifiers = [
            identifier
            for identifier in temp_identifiers
            if identifier not in curr_identifiers]

    return temp_identifiers


def get_infile_name(file_path: str) -> str:
    if "/" in file_path:
        infile_name = re.findall("(.*?).csv", file_path.split("/")[-1])[0]
    else:
        infile_name = re.findall("(.*?).csv", file_path.split("\\")[-1])[0]
    return infile_name


def request_twitter_objects(
    file_path: str, user_arg=True, tline_arg=True, irange=None
) -> None:
    api = get_twitter_api_instance()
    infile_name = get_infile_name(file_path)
    config = get_config(infile_name)

    try:
        user_identifiers = get_users_identifiers(file_path)
    except Exception as e:
        raise Exception(e)

    user_identifiers = filter_identifiers(user_identifiers, config, irange)

    for idx, identifier in enumerate(user_identifiers):
        if user_arg:
            try:
                begin = time.time()
                user = api.get_user(identifier)
                save_user_object(user, config)
                end = time.time()
                print("{} User {} object, success! => {:.2f}s".format(
                    (idx+1) % 100, identifier, end-begin))
            except tweepy.TweepError as e:
                print(e)
            except Exception as e:
                print(e)

        if tline_arg:
            if (idx+1) % 100 == 0:
                config = get_config(infile_name)
                print("======================================")
            try:
                begin = time.time()
                timeline = api.user_timeline(identifier, count=200)
                save_user_timeline(identifier, timeline, config)
                end = time.time()
                print("{} User {} timeline, success! => {:.2f}s".format(
                    (idx+1) % 100, identifier, end-begin))
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
        [json.dumps(user._json, ensure_ascii=False)], columns=["user_object"]
    )

    save_dataframe(
        df,
        config["USER_PATH"], config["USER_TABLE"]
    )


def save_user_timeline(
    identifier: int, timeline: object, config: dict
) -> None:
    objects = [
        [identifier, json.dumps(instance._json, ensure_ascii=False)]
        for instance in timeline
    ]
    df = pd.DataFrame(objects, columns=["id", "status_object"])

    save_dataframe(
        df,
        config["TIMELINE_PATH"], config["TIMELINE_TABLE"]
    )
