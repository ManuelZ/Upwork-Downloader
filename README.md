# Upwork downloader and visualizer

![User Interface](images/screenshot1.png)

## Summary

I started this project because I felt that I could personalize the way of finding good and fulfilling jobs in Upwork to my own needs and liking. 

My requirements are:
- I want to be able to find jobs that align with what I like to do.
- I want to reduce the time I spend on searching for interesting jobs.
- I want to be suggested for interesting jobs as quickly as possible.

So I decided to use Machine Learning for it to help with this endeavour.
This project consists of:

- A script to download jobs' data from Upwork (you need your own API key).
- A React user interface to go through the downloaded jobs and mark them as interesting or not.
- A Machine Learning setup to learn from the labeled jobs and classify unseen ones.
- TO BE DONE: automation of all the above steps.

## Setup Instructions

1. Clone this repository.

2. Request an API key from Upwork at https://www.upwork.com/services/api/apply.
   You can see your current available api keys in https://www.upwork.com/services/api/keys

3. Create a file `./api_key.secret`, with the following contents:

PUBLIC API KEY PROVIDED BY UPWORK
SECRET KEY PROVIDED BY UPWORK

4. Run `docker-compose up`


## Requirements

- The `python-upwork` package requires Python 3.8+
