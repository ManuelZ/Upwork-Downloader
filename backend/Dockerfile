FROM python:3.8-slim-buster

WORKDIR /code

COPY ./requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./backend/src ./src

ENV PYTHONPATH=/:/usr/lib/python3/dist-packages:$PYTHONPATH

# 
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

CMD [ "python", "src/backend.py" ] 
