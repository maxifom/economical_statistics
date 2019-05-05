FROM python:3.7.2-stretch
WORKDIR /usr/src/app
RUN apt-get update && apt-get install supervisor wget python-numpy libicu-dev gcc g++ libxml2-dev libxslt1-dev zlib1g-dev git default-libmysqlclient-dev cron -y
ADD ./supervisord/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./python/requirements.txt ./python/
RUN pip install --no-cache-dir -r ./python/requirements.txt
COPY ./crontab/crontab /etc/cron.d/
COPY ./docker/entrypoint.sh /
RUN chmod -R 777 /etc/cron.d/ /entrypoint.sh && crontab /etc/cron.d/crontab && export PYTHONPATH=$PYTHONPATH:/usr/src/app/python
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/usr/bin/supervisord","-c","/etc/supervisor/supervisord.conf"]