# Stocks Overview

> **_DISCLAIMER:_**  No warranty of any kind regarding correctness or loss of any information.

```text
Things your bank or broker should do for you. But if they don't...
```

This is a small command line tool that allows you to track your stock positions, including their buy or sell date.
For example, it can be helpful to know which and how many positions have been bought to manage your portfolio properly.

## How it works

Upon running the cli tool the first time, one is promted to create a

* config file (usually in the default app directory) and
* a data file (includes your actual stock information).

The config file contains no sensitive information and can be re-generated if required.

The data file will track all stock information that you enter. It is advised to keep this file private and also a
backup, in case a recovery is needed.
In case the file is corrupted or lost, all information are lost, too.


## Installation

* Install [pipx](https://pipx.pypa.io/stable/installation/) using `brew`.
* Install [poetry](https://python-poetry.org/docs/#installation) into pipx env
* Create and activate conda env
    ```shell
    mamba env create -f conda-environment.yml
    mamba activate stocks-overview
    ```
* Run `poetry install`
* Run the tool
    ```shell
    python src/stocks_overview/app/app.py --help
    ```
