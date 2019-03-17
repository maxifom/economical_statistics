FROM python:3.7.2-slim
WORKDIR /usr/src/app
COPY requirements-linux.txt ./requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends default-libmysqlclient-dev libicu-dev gcc g++-6 g++
RUN pip3 install -r requirements.txt
RUN apt-get install -y --no-install-recommends cron
RUN COPY ./crontab /etc/crontab
RUN chmod -R 777 ./ /etc/crontab && apt-get clean
ENV MYSQL_HOST=mysql
CMD ["ls"]