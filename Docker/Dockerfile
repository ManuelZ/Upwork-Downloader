# This image should have Python3.8 and Node 12
# It should first launch the npm run build process and then serve index.html 
# with Flask
FROM debian:buster-slim AS build

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    git gcc build-essential libssl1.1 libssl-dev zlib1g-dev ca-certificates \
    libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev curl wget

# Notice: weird problem with curl and TLS certificates.
# I need to manually update the cacert certificates using wget to let the 
# pyenv.run script (that uses curl) work.
ENV CURL_CA_BUNDLE /root/cacert.pem
RUN wget https://curl.haxx.se/ca/cacert.pem -O $CURL_CA_BUNDLE
ENV PYENV_ROOT /root/.pyenv
RUN curl https://pyenv.run | bash
ENV PATH $PYENV_ROOT/bin:$PATH
RUN pyenv install -v 3.8.6
RUN echo 'eval "$(pyenv init -)"' >> /root/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.bashrc

# pip builds
ENV PATH $PYENV_ROOT/versions/3.8.6/bin:$PATH
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    libatlas-base-dev liblapack-dev libopenblas-dev gfortran 
RUN pyenv virtualenv 3.8.6 myenv
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install numpy pandas scikit-learn scipy
RUN python -m pip install nltk
COPY ./backend/requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"



# The runtime-stage image; we can use Debian as the base image since the Conda
# env also includes Python for us.
FROM node:12-buster-slim AS runtime

# Copy /venv from the previous stage:
COPY --from=build /root/.pyenv /root/.pyenv
COPY --from=build /root/.bashrc /root/.bashrc
COPY --from=build /root/nltk_data /root/nltk_data

# To make requests to possible https endpoints work
RUN apt-get update && apt-get install --no-install-recommends -y libssl1.1 ca-certificates
# Other requirements
RUN apt-get install --no-install-recommends -y libopenblas-dev libgomp1 sqlite3

# Prepare pyenv's Python to be used
ENV PYENV_ROOT /root/.pyenv
ENV PATH $PYENV_ROOT/bin:$PATH
ENV PYENV_VERSION 3.8.6
ENV PATH $PYENV_ROOT/versions/3.8.6/bin:$PATH

# User-interface preparation
WORKDIR ./upwork-downloader-ui
RUN npm install -g pnpm
COPY ./upwork-downloader-ui/package.json .
RUN pnpm install
COPY ./upwork-downloader-ui/tailwind.config.js .
COPY ./upwork-downloader-ui/postcss.config.js .
COPY ./upwork-downloader-ui/src ./src
COPY ./upwork-downloader-ui/public ./public
RUN npm run build

# Backend preparation
WORKDIR /backend
COPY ./backend/src ./src
ENV PYTHONPATH=/backend:$PYTHONPATH
CMD [ "python", "src/backend.py" ] 

