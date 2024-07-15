  
#  FROM python:2.7
#  ENV PYTHONUNBUFFERED 1
#  RUN mkdir /code
#  WORKDIR /code
#  ADD requirements.txt /code/
#  RUN pip install -r requirements.txt
#  ADD . /code/
#  RUN chmod +x /code/docker-entrypoint.sh
#  ENTRYPOINT ["/code//docker-entrypoint.sh"]
# EXPOSE 5000

ARG PYTHON_VERSION=2.7

# ARG PYTHON_VERSION=3.10-slim-bullseye

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "vSD9d7IDft2zwqr5GVBWX1BRuqYEHEj2ONa2eW7mzhgMWi883s"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "crowdcoincoza.wsgi"]
