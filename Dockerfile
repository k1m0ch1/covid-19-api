FROM python:3.7-alpine
RUN apk add \
	--repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
	--no-cache \
	build-base libffi-dev python3-dev py3-lxml \
    libxml2 libxml2-dev libxslt-dev


RUN pip install --upgrade pip && pip install pipenv gunicorn

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY src/ ./src/
COPY manage.py ./manage.py

ENTRYPOINT ["python", "manage.py"]
