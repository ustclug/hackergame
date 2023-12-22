FROM python:3.11

RUN apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
WORKDIR /opt/hackergame
COPY requirements.txt /opt/hackergame/
RUN pip3 install --upgrade -r requirements.txt
# Bind project inside instead of copying it
# to avoid copying credentials inside container
# COPY ./ /opt/hackergame/

EXPOSE 2018
CMD ["docker/start.sh"]
