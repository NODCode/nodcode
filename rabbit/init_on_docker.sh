mkdir rabbit
cd rabbit
git clone https://github.com/harbur/docker-rabbitmq-cluster.git
cd docker-rabbitmq-cluster
docker build -t harbur/rabbitmq-cluster .
docker-compose up -d
cd ..
cd ..
rm -rf rabbit
docker exec -it dockerrabbitmqcluster_rabbit1_1 /bin/bash
rabbitmqctl set_policy ha-all "." '{"ha-mode":"all", "ha-sync-mode":"automatic"}'
exit



