# This image should have Python3.8 and Node 12
# It should first launch the npm run build process and then serve index.html 
# with Flask
FROM python:3.8-slim-buster  AS build

RUN apt-get update && apt-get install --no-install-recommends -y \
    git make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

RUN curl https://pyenv.run | bash

RUN ~/.pyenv/bin/pyenv init - && \
    ~/.pyenv/bin/pyenv virtualenv-init - && \
    ~/.pyenv/bin/pyenv install -v 3.8.6

# # The runtime-stage image; we can use Debian as the base image since the Conda
# # env also includes Python for us.
FROM debian:buster-slim AS runtime

# Copy /venv from the previous stage:
COPY --from=build /root/.pyenv /root/.pyenv

ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/bin:$PATH
RUN echo 'eval "$(pyenv init -)"' >> /root/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.bashrc

RUN pyenv global 3.8.6

SHELL ["/bin/bash", "-c"]

# # Source https://www.scivision.dev/compile-install-python-beta-raspberry-pi/
# RUN apt-get update && apt-get install --no-install-recommends -y libffi-dev libbz2-dev liblzma-dev libsqlite3-dev libncurses5-dev libgdbm-dev zlib1g-dev libreadline-dev libssl-dev tk-dev build-essential libncursesw5-dev libc6-dev openssl git wget ca-certificates

# WORKDIR backend

# COPY ./requirements.txt .

# RUN python -m pip install --no-cache-dir -r requirements.txt

# COPY ./backend/src ./src

# ENV PYTHONPATH=/:/usr/lib/python3/dist-packages:$PYTHONPATH

# RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"


# FROM debian:buster-slim AS runtime-image

# COPY --from=build /cpython-3.8.6 .

# CMD ["python"]

# # Install the package as normal:
# COPY environment.yml .
# RUN conda env create -f environment.yml

# # Install conda-pack:
# RUN conda install -c conda-forge conda-pack

# # Use conda-pack to create a standalone environment in /venv:
# RUN conda-pack -n example -o /tmp/env.tar && \
#   mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
#   rm /tmp/env.tar

# # We've put venv in same path it'll be in final image, so now fix up paths:
# RUN /venv/bin/conda-unpack


# # The runtime-stage image; we can use Debian as the base image since the Conda
# # env also includes Python for us.
# FROM debian:buster-slim AS runtime

# # Copy /venv from the previous stage:
# COPY --from=build /venv /venv

# # When image is run, run the code with the environment activated:
# SHELL ["/bin/bash", "-c"]
# ENTRYPOINT source /venv/bin/activate && python -c "import numpy; print('success!')"


# # At the time of writing this, the apt version of numpy was compiled against
# # Python 3.7, but I need to use it with Python. An error was popping due to that. 
# # RUN apt-get update && apt-get install --no-install-recommends -y

# COPY ./requirements.txt .
# RUN python -m pip install --no-cache-dir -v -r requirements.txt

# COPY ./src ./src

# ENV PYTHONPATH=/:/usr/lib/python3/dist-packages:$PYTHONPATH

# # RUN python -c "import nltk; nltk.download('stopwords')"

# # CMD [ "python", "src/backend.py" ] 
