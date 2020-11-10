FROM python:3.8

WORKDIR /code

COPY ./requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY ./src ./src

ENV PYTHONPATH=/code

RUN python -c "import nltk; nltk.download('stopwords')"

CMD [ "python", "src/backend.py" ] 
