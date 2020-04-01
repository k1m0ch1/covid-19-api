FROM python:3.7-alpine
RUN apk add \
	--repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
	--no-cache \
	build-base libffi-dev python3-dev py3-lxml \
    libxml2 libxml2-dev libxslt-dev postgresql-dev openssh git \
	libxml2-dev libxslt-dev chromium-chromedriver chromium file \
	imagemagick bash pngcrush optipng=0.7.7-r0 imagemagick-dev

RUN pip install --upgrade pip && pip install pipenv gunicorn

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY src/ ./src/
COPY manage.py ./manage.py

ENV PATH="/usr/bin/chromedriver:${PATH}"
ENV CHROMEDRIVER="/usr/bin/chromedriver"

ENTRYPOINT ["python", "manage.py"]
