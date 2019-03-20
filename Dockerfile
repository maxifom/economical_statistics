FROM python:3.7.2-stretch
WORKDIR /usr/src/app
RUN apt-get update && apt-get install supervisor wget python-numpy libicu-dev gcc g++ libxml2-dev libxslt1-dev zlib1g-dev git default-libmysqlclient-dev cron -y
COPY ./download-csv-archive.sh ./
RUN bash ./download-csv-archive.sh
ADD ./supervisord/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./python/requirements.txt ./python/
RUN pip install --no-cache-dir -r ./python/requirements.txt
RUN polyglot download sentiment2.ru
COPY ./crontab/crontab /etc/cron.d/
COPY ./docker/entrypoint.sh /
COPY ./data/companies.pickle ./data/
RUN chmod -R 777 /etc/cron.d/ /entrypoint.sh && crontab /etc/cron.d/crontab
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord","-c","/etc/supervisor/supervisord.conf"]