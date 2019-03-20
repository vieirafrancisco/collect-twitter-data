import os
import argparse

import utils


def create_configkey_file():
    default_content = ["CONSUMER_KEY", "CONSUMER_SECRET",
                       "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
    with open("config.key.yaml", "w") as ck_file:
        for row in default_content:
            ck_file.write(row+': ""\n')


def get_commandline_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--in', dest='infile', nargs='?', type=str
    )
    parser.add_argument(
        '--ckey', nargs='?',
        type=string_to_bool_type, default=False
    )
    parser.add_argument(
        '--user', nargs='?',
        type=string_to_bool_type,
        const=True, default=True
    )
    parser.add_argument(
        '--tline', nargs='?',
        type=string_to_bool_type,
        const=True, default=True
    )
    parser.add_argument(
        '--range', nargs=2, type=int
    )

    return parser.parse_args()


def string_to_bool_type(arg: str) -> bool:
    if arg.lower() in ['true', 't', '1']:
        return True
    elif arg.lower() in ['false', 'f', '0']:
        return False
    else:
        raise argparse.ArgumentTypeError("Argument need to me boolean!")


if __name__ == '__main__':
    args = get_commandline_arguments()

    # if needs to create a config key file
    if args.ckey:
        if "config.key.yaml" not in os.listdir('.'):
            create_configkey_file()
        else:
            print("already exist this file")

    if not (args.tline or args.user):
        raise Exception("tline and user argument can't be both False")

    utils.request_twitter_objects(
        args.infile, args.user, args.tline, args.range
    )
