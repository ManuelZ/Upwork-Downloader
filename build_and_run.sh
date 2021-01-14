#!/bin/bash
# Modified from: https://pythonspeed.com/articles/faster-multi-stage-builds/

git pull

set -euo pipefail
# Pull the latest version of the image, in order to populate the build cache
docker pull mclzc/private-repo:ud_compile_stage || true
docker pull mclzc/private-repo:ud_image         || true

# Build the compile stage
docker build --target build -f ./Docker/Dockerfile \
             --cache-from=mclzc/private-repo:ud_compile_stage \
             --tag mclzc/private-repo:ud_compile_stage .

# Build the runtime stage, using cached compile stage
docker build --target runtime -f ./Docker/Dockerfile \
             --cache-from=mclzc/private-repo:ud_compile_stage \
             --cache-from=mclzc/private-repo:ud_image \
             --tag mclzc/private-repo:ud_image .

# Push the new versions
docker push mclzc/private-repo:ud_compile_stage
docker push mclzc/private-repo:ud_image

docker stop ud_container
docker rm ud_container
docker create -it --name ud_container --volume="/home/pi/:/code" ud_image
sudo docker container start --interactive -p 5000:5000 ud_container


