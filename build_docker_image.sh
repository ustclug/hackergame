TAG=`cat version.txt`

docker build --no-cache -t hackergame-backend:$TAG -f deploy/Dockerfile .
docker build --no-cache -t hackergame-nginx:$TAG -f deploy/Dockerfile_nginx .