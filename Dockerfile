FROM python:3.9-slim

WORKDIR /app

RUN apt-get update

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install firefox

RUN playwright install-deps firefox

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
