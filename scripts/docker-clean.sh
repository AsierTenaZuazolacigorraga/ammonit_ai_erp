cd "$(dirname "$0")"
cd ..
if [ "$(docker ps -aq)" ]; then
    docker stop $(docker ps -aq)
fi
docker rm $(docker ps -aq)
docker rmi $(docker images -q) 
# docker volume rm $(docker volume ls -q) 
# docker network rm $(docker network ls -q) 
docker builder prune --all --force