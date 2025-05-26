FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/www/app/static/ktm
RUN mkdir -p /var/www/app/static/products
RUN mkdir -p /var/www/app/static/jastip
RUN mkdir -p /var/www/app/static/anjem
RUN mkdir -p /var/www/app/static/anjem/chat
COPY . /var/www/app
WORKDIR /var/www/app

RUN pip install pipenv
RUN pipenv --python /usr/local/bin/python3.11
RUN pipenv install --system --deploy
# RUN pipenv run flask --app manage db init
# RUN pipenv run flask --app manage db migrate
# RUN pipenv run flask --app manage db upgrade

# CMD ["pipenv", "run", "flask", "--app", "app", "run"]
# Define the command to run your application
RUN pip install gunicorn
EXPOSE 8000 
CMD ["pipenv", "run", "gunicorn", "-b", "0.0.0.0:8000", "app:app"]