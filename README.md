# GitHub labels replace tool

Find & replace labels in GitHub issues and pull requests

## Configure GitHub token

This tool requires a GitHub token to be set in `GH_TOKEN` environment variable. You can generate a token in your GitHub account settings:

1. Go to [Github settings -> Developer settings](https://github.com/settings/apps)
2. Click [Personal access tokens -> Tokens (classic)](https://github.com/settings/tokens)
3. Click "Generate new token"
4. Create a token with `repo` permissions (or `public_repo` if you're only going to use it with public repositories)
5. Copy the token and set it in `GH_TOKEN` environment variable, or pass it as a command line parameter (see example below)

## Usage

```bash
$ python3 gh-label-replace.py [params] <owner> <repo> <old_labels> <new_labels>
```

Parameters:
- `-s` `--start-date` - start date in YYYY-MM-DD format
- `-o` `--overwrite` - overwrite all existing labels completely
- `-d` `--dry-run` - do not actually change anything, just print what would be done
- `owner` - GitHub repository owner/organization
- `repo` - GitHub repository name
- `old_labels` - comma-separated list of old labels
- `new_labels` - comma-separated list of new labels

Example:

```bash
$ GH_TOKEN='exampleToken' python3 gh-label-replace.py --start-date=2020-01-01 trustmaster gh-labels-replace "bug,enhancement" "bug,feature"
```
