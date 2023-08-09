# GitHub labels replace tool

Find &amp; replace labels in GitHub Pull Requests

## Usage

```bash
$ python3 gh-label-replace.py --start-date=<date> <owner> <repo> <old_labels> <new_labels>
```

Parameters:
- `--start-date` - start date in YYYY-MM-DD format
- `owner` - GitHub repository owner/organization
- `repo` - GitHub repository name
- `old_labels` - comma-separated list of old labels
- `new_labels` - comma-separated list of new labels

Example:

```bash
$ python3 gh-label-replace.py --start-date=2020-01-01 trustmaster gh-labels-replace "bug,enhancement" "bug,feature"
```
