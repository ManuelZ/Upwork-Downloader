FROM python:3.8-slim-buster

WORKDIR /code

COPY ./requirements.txt .
# RUN python -m pip install --no-cache-dir -v -r requirements.txt

# Installing Numpy through pip compiles it... better just download it like here
RUN apt-get install python3-numpy python3-pandas python3-sklearn python3-nltk python3-flask python3-flask-cors

COPY ./src ./src

ENV PYTHONPATH=/code

RUN python -c "import nltk; nltk.download('stopwords')"

CMD [ "python", "src/backend.py" ] 
