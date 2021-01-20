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
    git clone https://github.com/ManuelZ/Upwork-Downloader

2. (Request an API key)[https://www.upwork.com/services/api/apply] from Upwork
   You can see your current available api keys in https://www.upwork.com/services/api/keys

3. Create a file `./api_key.secret` in your local machine, with the following contents:
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

## Setup instructions

Download a Raspberry Pi image and burn it to a microSD card:
[Raspberry Pi OS](https://www.raspberrypi.org/downloads/raspberry-pi-os/)

### Add an empty file named "ssh" to the boot partition.


Login into the Raspberry
[Obtain Raspberry Pi IP](https://www.raspberrypi.org/documentation/remote-access/ip-address.md)
[Official SSH guide](https://www.raspberrypi.org/documentation/remote-access/ssh/README.md)


    ssh raspberrypi.local -l pi

The default password is "raspberry"

### Configure the Wifi and change the local time/change timezone
    sudo raspi-config

### Setup a static ip
    sudo nano /etc/dhcpcd.conf

Uncomment and modify the following fields: `interface`, `ip_address`, `routers`
- For 'interface' set wlan0
- For 'ip_address' put 192.168.1.10
- For 'routers' put 192.168.1.1

### Reload the connection
    sudo wpa_cli -i wlan0 reconfigure

### Confirm your static ip
    ifconfig wlan0

### Update packages (you may as well just skip this)
    sudo apt-get update && sudo apt-get -y upgrade

### Install git
    sudo apt-get install -y --no-install-recommends git

### Clean the apt cache
    sudo apt-get clean

### Generate a new SSH key (do not set a passphrase):
    ssh-keygen -t ed25519 -C "your_email@example.com"

### Start the ssh agent:
    eval "$(ssh-agent -s)"
   
### Add the SSH private key to the ssh-agent:
    ssh-add ~/.ssh/id_ed25519

### Copy the contents from here
    cat ~/.ssh/id_ed25519.pub

### Use the copied contents to the ssh key to Github
    https://docs.github.com/en/free-pro-team@latest/articles/adding-a-new-ssh-key-to-your-github-account

### Clone repo
    git clone https://github.com/ManuelZ/Upwork-Downloader

### Change directory into the project
    cd ~/Upwork-Downloader
### Add a ssh remote
    git remote set-url origin git@github.com:ManuelZ/Upwork-Downloader.git
### Add your Upwork API key (run this from your local machine)
    scp api_key.secret pi@raspberrypi.local:/home/pi/Upwork-Downloader/



### Install Docker (may take some time)
    curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh

[Official Docker installation instructions](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script)

### Allow your user to fully use Docker
    sudo usermod -aG docker pi

### Restart the docker service
    sudo /etc/init.d/docker stop
    sudo /etc/init.d/docker start

### Setup DockerHub 
Create an account in DockerHub, create a personal private repository and create an access token.
 - https://docs.docker.com/docker-hub/access-tokens/#create-an-access-token

### Login into DockerHub
    docker login --username mclzc --password YOUR_TOKEN

## Compilation instructions 
### Change CONF_SWAPSIZE to 2048
    sudo nano /etc/dphys-swapfile

### Restart the swap service
    sudo /etc/init.d/dphys-swapfile stop
    sudo /etc/init.d/dphys-swapfile start

REMEMBER TO GET IT BACK TO 100MB AFTER COMPILING OR YOUR MICROSD WILL DIE EARLY

### Change directory into the project
    cd ~/Upwork-Downloader
### Run the compilation
    bash build_and_run.sh

<!-- 
### Build the image
    sudo docker image build -f ./Docker/Dockerfile -t ud_image .

### Create the container
    sudo docker create -it --name ud_container --volume="/home/pi/:/code" ud_image

### Run the container
    sudo docker run -p 5000:5000 ud_image

TOKEN: 6a9a185c-40a0-47bf-bf52-0ef15b0b7f4c
docker push mclzc/private-repo:latest


THE FOLLOWING IS NOT REALLY A GOOD IDEA

docker buildx create --name mybuilder
docker buildx use mybuilder
docker buildx inspect --bootstrap
docker buildx build --push --platform linux/arm/v7 --tag mclzc/ud_image -f ./Docker/Dockerfile .
 


# Run "cat /proc/cpuinfo" to obtain information about your exact model
# https://elinux.org/RPi_HardwareHistory

# During the first push of a new branch
git push -u origin hourly_rate


 -->


