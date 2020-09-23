FROM python:3.8-slim-buster

COPY ./backend /app/backend
COPY ./deploy /app/deploy
WORKDIR /app/backend

RUN python -m pip install -U pip && \
    pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 8000
ENTRYPOINT /app/deploy/entrypoint.sh