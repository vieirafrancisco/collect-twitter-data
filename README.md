<h1 align="center">Collect Twitter Data</h1>

## Description:
Script to collect data from Twitter, with Twitter's API using python's [Tweepy](https://www.tweepy.org/) library.

## Requirements:

* [pipenv](https://pipenv.readthedocs.io/en/latest/)

```console
pip install pipenv
```

## Usage:

Clone:

```console
git clone https://github.com/vieirafrancisco/collect-twitter-data.git
```

Install dependences:

```console
cd ./collect-twitter-data

pipenv install && pipenv shell
```

Create config key file to insert the credentials from twitter's api access:

```console
pipenv run createkey
```

Open **config.key.yaml** file, you will see like that:

```yaml
CONSUMER_KEY: ""
CONSUMER_SECRET: ""
ACCESS_TOKEN: ""
ACCESS_TOKEN_SECRET: ""
```

Just go to the [twitter application management](https://developer.twitter.com/en/apps) to get this credentials!

To use this script you need a csv with a column named **id** with user's ids in the rows. With this file in hands just link the path like that:

```console
python main.py --infile=paste/the/file/path/file_name.csv
```

Then the script will be running and the output will be stored in the **resultset/** folder :tada:.

## Contribution:
Any contribution will be helpful, just create a issue or a pull request!
