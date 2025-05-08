# Sapi 🐮

> [!NOTE]
> `Sapi` is currently being developed.

`sapi` is a command-line-interface (CLI) program to answer this specific question:

> How many articles does X have in year Y to Z? Can you also extract X's paper citation per year?
> We use google scholar data.

_Yes_, `sapi` use [Google Scholar](https://scholar.google.com/) data to extract the answers.

Also _yes_, it's **not as sophisticated as AI-based crawler**. So lower your expectations.

And lastly _yes_. It's written in Python and _heavily_ rely on:

1. [Python's selenium-binding](https://selenium-python.readthedocs.io/)
2. [Beautiful Soup's parsing engine](https://pypi.org/project/beautifulsoup4/)

`sapi` is chosen to be the name of the project just because this type of questions get asked too many times and it's exhausting to collect more and more unmanageable data.

# Usage

## Examples

```bash
uv run .\main.py --scholar-id <scholar_id> --year 2020:2025 --verbose --save-path out.csv
```

## Available options

| Options      | Short | Desc                                                                    |
| ------------ | ----- | ----------------------------------------------------------------------- |
| --scholar-id | -s    | Google scholar's ID                                                     |
| --year       | -y    | Year range. Can be written as "2020" or in range format e.g."2020:2023" |
| --verbose    | -v    | Display all the logs                                                    |
| --save-path  | -o    | The path to save the .csv output                                        |
| --overwrite  |       | Overwrite existing .csv                                                 |
| --help       |       | Show help                                                               |

---

`sapi` by I Gede Teguh Satya Dharma: 2025.
