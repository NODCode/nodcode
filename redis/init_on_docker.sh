mkdir redis
cd redis
git clone https://github.com/Grokzen/docker-redis-cluster
cd docker-redis-cluster/
docker-compose -f compose.yml build
docker-compose -f compose.yml up
