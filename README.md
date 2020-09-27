# Hackergame CTF 比赛平台

## 文档
[需求](docs/demands.md)

[后端](docs/backend.md)

[接口](docs/interfaces.md)

## Docker
构建后端:
```bash
docker build --no-cache -t hackergame-backend:[TAG] -f deploy/Dockerfile .
```

构建 nginx:
```bash
docker build --no-cache -t hackergame-nginx:TAG -f deploy/Dockerfile_nginx .
```
