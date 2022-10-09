FROM python:3.9

RUN apt-get update && \
    apt-get -y install uwsgi-plugin-python3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
WORKDIR /opt/hackergame
COPY requirements.txt /opt/hackergame/
RUN pip3 install --upgrade -r requirements.txt
COPY ./ /opt/hackergame/

CMD ["/usr/bin/uwsgi", "--master", "--ini", "conf/uwsgi-apps/hackergame-docker.ini"]
