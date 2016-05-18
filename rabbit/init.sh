##-------------------Requirements---------------------------
##   1. Download RabbitMQ from: 
##    http://www.rabbitmq.com/releases/rabbitmq-server/v3.6.1/rabbitmq-server_3.6.1-1_all.deb

#-----------------------Script-------------------------------

sudo rabbitmq-plugins rabbitmq_management enable
sudo service rabbitmq-server start
sudo rabbitmqctl start_app
sudo RABBITMQ_NODE_PORT=5672 RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,15672}]" RABBITMQ_NODENAME=rabbit rabbitmq-server -detached
sudo RABBITMQ_NODE_PORT=5673 RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,15673}]" RABBITMQ_NODENAME=hare rabbitmq-server -detached
sudo RABBITMQ_NODE_PORT=5674 RABBITMQ_SERVER_START_ARGS="-rabbitmq_management listener [{port,15674}]" RABBITMQ_NODENAME=hare2 rabbitmq-server -detached
sudo rabbitmqctl -n hare stop_app
sudo rabbitmqctl -n hare2 stop_app
sudo rabbitmqctl -n hare join_cluster rabbit@`hostname -s`
sudo rabbitmqctl -n hare2 join_cluster rabbit@`hostname -s`
sudo rabbitmqctl -n hare start_app
sudo rabbitmqctl -n hare2 start_app
sudo rabbitmqctl set_policy ha-all "." '{"ha-mode":"all", "ha-sync-mode":"automatic"}'
sudo rabbitmqctl cluster_status



