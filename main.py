import os
import sys
import argparse

import yaml
import tweepy


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


def create_configkey_file():
    default_content = ["CONSUMER_KEY", "CONSUMER_SECRET",
                       "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
    with open("config.key.yaml", "w") as ck_file:
        for row in default_content:
            ck_file.write(row+': ""\n')


def get_commandline_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--in', dest='infile', nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin
    )
    parser.add_argument(
        '--cokey', dest='confkey', nargs='?',
        type=bool,
        default=False
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = get_commandline_arguments()

    # if needs to create a config key file
    if args.confkey:
        if "config.key.yaml" not in os.listdir('.'):
            create_configkey_file()
        else:
            print("already exist this file")

    api = get_twitter_api_instance()
