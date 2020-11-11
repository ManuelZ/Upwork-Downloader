FROM continuumio/miniconda3 AS build

# Source: https://pythonspeed.com/articles/conda-docker-image-size/

# Install the package as normal:
COPY environment.yml .
RUN conda env create -f environment.yml

# Install conda-pack:
RUN conda install -c conda-forge conda-pack

# Use conda-pack to create a standalone environment in /venv:
RUN conda-pack -n example -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

# We've put venv in same path it'll be in final image,
# so now fix up paths:
RUN /venv/bin/conda-unpack

# The runtime-stage image; we can use Debian as the
# base image since the Conda env also includes Python
# for us.
FROM python:3.8-slim-buster AS runtime

# Copy /venv from the previous stage:
COPY --from=build /venv /venv

# When image is run, run the code with the environment
# activated:
SHELL ["/bin/bash", "-c"]
ENTRYPOINT source /venv/bin/activate && \
           python -c "import numpy; print('success!')"


# # At the time of writing this, the apt version of numpy was compiled against
# # Python 3.7, but I need to use it with Python. An error was popping due to that. 
# # RUN apt-get update && apt-get install --no-install-recommends -y

# COPY ./requirements.txt .
# RUN python -m pip install --no-cache-dir -v -r requirements.txt

# COPY ./src ./src

# ENV PYTHONPATH=/:/usr/lib/python3/dist-packages:$PYTHONPATH

# # RUN python -c "import nltk; nltk.download('stopwords')"

# # CMD [ "python", "src/backend.py" ] 
