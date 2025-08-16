FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

COPY data/data.csv data/data.csv
COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --deploy --ignore-pipfile --system

COPY IT_team_assistance .

EXPOSE 5000

CMD uvicorn app:app --host 0.0.0.0 --port 5000