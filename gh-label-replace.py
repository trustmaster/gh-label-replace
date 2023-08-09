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
from urllib.parse import quote


@dataclass
class Params:
    """Struct to pass parameters to functions"""
    owner: str
    repo: str
    old_labels: list[str]
    new_labels: list[str]
    start_date: str
    overwrite: bool
    dry_run: bool

    def __init__(self,
                 owner: str,
                 repo: str,
                 old_labels: str,
                 new_labels: str,
                 start_date: str = '',
                 overwrite: bool = False,
                 dry_run: bool = False):
        self.owner = owner
        self.repo = repo
        self.old_labels = [l.strip() for l in old_labels.split(',')]
        self.new_labels = [l.strip() for l in new_labels.split(',')]
        self.start_date = start_date
        self.overwrite = overwrite
        self.dry_run = dry_run


def urlsafe(labels: list[str]) -> str:
    return quote(','.join(labels))


def get_pull_requests(headers: dict, p: Params, page: int = 1) -> list[dict]:
    """Gets a list of issues from GitHub API as a list of dict objects or returns an empty list"""

    labels = urlsafe(p.old_labels)
    url = f'https://api.github.com/repos/{p.owner}/{p.repo}/issues?state=all&labels={labels}&per_page=100&page={page}'

    if p.start_date != None and p.start_date != '':
        url += f'&since={p.start_date}'

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    json = response.json()
    return [pr for pr in json]


def update_pull_request(headers: dict, p: Params, pr: dict):
    """Updates an issue with new labels"""

    labels = p.new_labels
    existing_labels = [l['name'] for l in pr['labels']]
    if not p.overwrite:
        # Remove old labels from existing labels
        labels = [l for l in existing_labels if l not in p.old_labels]
        labels += p.new_labels

    url = f'https://api.github.com/repos/{p.owner}/{p.repo}/issues/{pr["number"]}'
    data = {'labels': labels}

    if not p.dry_run:
        response = requests.patch(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

    print(f'Updated #{pr["number"]} replacing', existing_labels, 'with',
          labels)


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
    'Replaces labels on GitHub issues and pull requests in a repo with other labels. By default only the provided labels are changed, other labels remain untouched.'
)
parser.add_argument('owner', type=str, help='GitHub repo owner')
parser.add_argument('repo', type=str, help='GitHub repo in format owner/repo')
parser.add_argument('old_labels',
                    type=str,
                    help='Old labels in a PR, separated by commas')
parser.add_argument('new_labels',
                    type=str,
                    help='New labels to replace with, separated by commas')
parser.add_argument('-s',
                    '--start-date',
                    type=str,
                    help='Start date to filter pull requests by')
parser.add_argument('-o',
                    '--overwrite',
                    action='store_true',
                    help='Overwrite all existing labels')
parser.add_argument('-d',
                    '--dry-run',
                    action='store_true',
                    help='Dry run, don\'t update any issues')
args = parser.parse_args()

repo = args.repo
params = Params(args.owner, args.repo, args.old_labels, args.new_labels,
                args.start_date, args.overwrite, args.dry_run)

# Iterate through pages of pull requests
try:
    page = 1
    while True:
        prs = get_pull_requests(headers, params, page)
        if len(prs) == 0:
            break

        for pr in prs:
            update_pull_request(headers, params, pr)

        page += 1
except requests.exceptions.HTTPError as e:
    print(e)
    sys.exit(1)
