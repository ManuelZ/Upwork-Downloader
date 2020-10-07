# Upwork downloader and visualizer

![User Interface](images/screenshot1.png)

## Summary

This project consists of:

- A script to download jobs' data from Upwork based on an input query.
- An [Electron](https://www.electronjs.org/) user interface to go through the downloaded jobs and mark them as interesting or not.
- A Machine Learning setup to learn from the labeled jobs and classify unseen ones.

## Setup Instructions

0. Clone this repository.

1. Request an API key from Upwork at https://www.upwork.com/services/api/apply.
   You can see your current available api keys in https://www.upwork.com/services/api/keys

2. Create a file `./api_key.secret`, with the following contents:

```
PUBLIC API KEY PROVIDED BY UPWORK
SECRET KEY PROVIDED BY UPWORK
```

3. Run the `upwork_downloader.py` file. The output data will be saved in `./data/data.csv`.

4. Change directory into `./upwork-downloader-ui` and follow the `README` instructions.

## Requirements

- The `python-upwork` package requires Python 3.8+

### TODOs:

- Get the ids from the saved jobs page and create a function to retrieve
  all the information of such jobs with the API.
