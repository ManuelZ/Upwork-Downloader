FROM python:3.8-slim-buster


# At the time of writing this, the apt version of numpy was compiled against
# Python 3.7, but I need to use it with Python. An error was popping due to that. 
RUN apt-get update && apt-get install --no-install-recommends -y python3-nltk python3-flask python3-flask-cors

COPY ./requirements.txt .
RUN python -m pip install --no-cache-dir -v -r requirements.txt

COPY ./src ./src

ENV PYTHONPATH=/:/usr/lib/python3/dist-packages:$PYTHONPATH

# RUN python -c "import nltk; nltk.download('stopwords')"

# CMD [ "python", "src/backend.py" ] 
