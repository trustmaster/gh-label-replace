#!python3
# Replaces labels on GitHub pull requests in a repo that have given label(s).
# Requires a GitHub personal access token with repo permissions passed in GH_TOKEN env variable.
# https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line
# Usage: python3 gh-label-replace.py --start-date=<date> <owner> <repo> <old_labels> <new_labels>

import argparse
import os
import sys
import requests
import json

from dataclasses import dataclass
from typing import Generator


@dataclass
class Params:
    """Struct to pass parameters to functions"""
    owner: str
    repo: str
    old_labels: str
    new_labels: str
    start_date: str

    def __init__(self, owner: str, repo: str, old_labels: str, new_labels: str,
                 start_date: str):
        self.owner = owner
        self.repo = repo
        self.old_labels = old_labels
        self.new_labels = new_labels
        self.start_date = start_date


def get_pull_requests(headers: dict, p: Params, page: int = 1) -> list[dict]:
    """Gets a list of pull requests from GitHub API as a list of dict objects or returns an empty list"""

    url = f'https://api.github.com/repos/{p.owner}/{p.repo}/pulls?state=all&labels={p.old_labels}&since={p.start_date}&per_page=100&page={page}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    json = response.json()
    return [pr for pr in json]


def update_pull_request(headers: dict, p: Params, number: int):
    """Updates a pull request with new labels"""

    url = f'https://api.github.com/repos/{p.owner}/{p.repo}/pulls/{number}'
    data = {'labels': p.new_labels.split(',')}

    response = requests.patch(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()


# Get GitHub token from env variable
token = os.environ.get('GH_TOKEN')
if not token:
    exit(
        'Error: please set GH_TOKEN env variable with a GitHub personal access token with repo permissions'
    )

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {token}',
    'X-GitHub-Api-Version': '2022-11-28'
}

parser = argparse.ArgumentParser(
    description=
    'Replaces labels on GitHub pull requests in a repo that have a given label.'
)
parser.add_argument('owner', type=str, help='GitHub repo owner')
parser.add_argument('repo', type=str, help='GitHub repo in format owner/repo')
parser.add_argument('old_labels',
                    type=str,
                    help='Old labels in a PR, separated by commas')
parser.add_argument('new_labels',
                    type=str,
                    help='New labels to replace with, separated by commas')
parser.add_argument('-d',
                    '--start-date',
                    type=str,
                    help='Start date to filter pull requests by')
args = parser.parse_args()

repo = args.repo
params = Params(args.owner, args.repo, args.old_labels, args.new_labels,
                args.start_date)

# Iterate through pages of pull requests
try:
    page = 1
    while True:
        prs = get_pull_requests(headers, params, page)
        if len(prs) == 0:
            break

        for pr in prs:
            update_pull_request(headers, params, pr['number'])
            print(f'Updated PR #{pr["number"]} in {repo}')

        page += 1
except requests.exceptions.HTTPError as e:
    print(e)
    sys.exit(1)
