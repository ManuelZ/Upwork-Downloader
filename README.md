# Upwork downloader and visualizer

## Summary

This project consists of:

- A script to download jobs data from upwork based in an input query,
- An Electron user interface to go through the downloaded jobs and mark them as interesting or not.
- A Machine Learning setup to learn from the labeled projects and classify unseen ones.

## Instructions

1. Request an API key from Upwork at https://www.upwork.com/services/api/apply.
   You can see your current available api keys in https://www.upwork.com/services/api/keys

2. Create an `api_key.secret` file with the following contents:

```
PUBLIC API KEY PROVIDED BY UPWORK
SECRET KEY PROVIDED BY UPWORK
```

3. Run the `upwork_downloader.py` file. The output data will be saved in `./data/data.csv`.

4. Change directory into `./upwork-downloader-ui` and follow the `README` instructions (which are basically running `npm run` and `npm run electron`).

### TODOs:

- Get the ids from the saved jobs page and create a function to retrieve
  all the information of such jobs with the API.
