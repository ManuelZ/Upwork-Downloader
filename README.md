# Upwork automatic jobs classifier

![User Interface 1](images/image1.png)

## Summary

I started this project because I felt that I could personalize the way of finding good and fulfilling jobs in Upwork to my own needs and liking. 

My requirements are:
- I want to be able to find jobs that align with what I like to do.
- I want to reduce the time I spend on searching for interesting jobs.
- I want to be suggested for interesting jobs as quickly as possible.

So I decided to use Machine Learning for it to help with this endeavor.
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

4. Edit the file `upwork-downloader-ui/src/config.js` and make the production endpoint point to your desired internal network IP.

5. Run `docker-compose build --parallel && docker-compose up`


## Requirements

- The `python-upwork` package requires Python 3.8+

## Note
According to the [Upwork's API Terms of Use](https://www.upwork.com/legal#api), section 3, a project like this one is permitted:

```
Permitted Uses of the Upwork API. Your use of the Upwork API is limited to the purpose of facilitating your own or your Users’ use of the Upwork Site and Site Services. Some examples of permitted uses of the Upwork API would be to create Applications that:

Allow Upwork Users to search for and browse Upwork job postings with a customized interface;
...
```

## Technologies used:
- Python
- Flask
- Sqlite3
- Scikit-learn
- Pandas
- ReactJS (Hooks)
- TailwindCSS
- Docker

## Raspberry Pi instructions

Download a Raspberry Pi image and burn it to a microSD card:
[Raspberry Pi OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/)

### Add an empty file named "ssh" to the boot partition.


Login into the Raspberry
[Obtain Raspberry Pi IP](https://www.raspberrypi.org/documentation/remote-access/ip-address.md)
[Official SSH guide](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md)


    ssh raspberrypi.local -l pi

The default password is "raspberry"

### Configure the Wifi
    sudo raspi-config

### Setup a static ip
    sudo nano /etc/dhcpcd.conf

Uncomment and modify the following fields: `interface`, `ip_address`, `routers`

### Reload the connection
    sudo wpa_cli -i wlan0 reconfigure

### Confirm your static ip
    ifconfig wlan0

### Update packages (you may as well just skip this)
    sudo apt-get update && sudo apt-get -y upgrade

### Install git
    sudo apt-get install -y git

### Clean the apt cache
    sudo apt-get clean

### Change local time/change timezone
   sudo raspi-config

<!-- ### Install Pip and Numpy
    sudo apt install python3-pip python3-numpy -->

### Clone repo
    git clone https://github.com/ManuelZ/Upwork-Downloader

### Add your Upwork API key (run this from your local machine)
    scp api_key.secret pi@raspberrypi.local:/home/pi/Upwork-Downloader/

<!-- ### Install requirements
     python3 -m pip install -r requirements.txt -->

<!-- ### Prepare nltk requirements
    python3 -c "import nltk; nltk.download('stopwords')"

### Add PYTHONPATH
    echo "PYTHONPATH=~/Upwork-Downloader:$PYTHONPATH" >> ~/.bashrc -->
    
## Install Docker

[Official instructions](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script)

    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
    sudo usermod -aG docker pi

### Change directory
    cd ~/Upwork-Downloader

### Build the image
    docker image build -f ./Dockerfile -t ud_image .

### Create the container
    docker create -it --name ud_container --volume="/home/pi/:/code" ud_image

### Run the container
    docker run -p 5000:5000 ud_image




<!-- 
Once inside, generate a new SSH key:

    ssh-keygen -t ed25519 -C "your_email@example.com"


Start the ssh agent:
    eval "$(ssh-agent -s)"
    Agent pid 1121
   
Add the SSH private key to the ssh-agent:
    ssh-add ~/.ssh/id_ed25519

[Add the generated key to your the Github account](https://docs.github.com/en/free-pro-team@latest/articles/adding-a-new-ssh-key-to-your-github-account)
 -->