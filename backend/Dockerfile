FROM python:3.8-slim-buster

WORKDIR /code

COPY ./requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./backend/src ./src

ENV PYTHONPATH=/:/usr/lib/python3/dist-packages:$PYTHONPATH

RUN python -c "import nltk; nltk.download('stopwords')"

RUN pwd
RUN ls

CMD [ "python", "src/backend.py" ] 
