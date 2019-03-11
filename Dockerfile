FROM python:3.7.2-alpine3.9
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add make automake gcc g++ subversion python3-dev
RUN apk add libffi-dev
RUN apk add libmysqlclient-dev
RUN pip install -r requirements.txt

ENV MYSQL_HOST=mysql

CMD ["ls"]