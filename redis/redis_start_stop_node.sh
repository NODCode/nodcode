sudo docker exec -it DOCKER_CONTAINER_NAME /bin/bash
supervisorctl stop redis-1 #stop node on port 7000
supervisorctl start redis-1

supervisorctl stop redis-2 #stop node on port 7001
supervisorctl start redis-2

supervisorctl stop redis-5 #stop node on port 7004
supervisorctl start redis-5








