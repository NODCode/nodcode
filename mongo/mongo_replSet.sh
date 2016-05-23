docker network create --subnet=172.18.0.0/16 mynet123

docker run --net mynet123 --ip 172.18.0.11 --name mongo1 -p 27018:27017 -d mongo --enableMajorityReadConcern --replSet rs001

docker run --net mynet123 --ip 172.18.0.12 --name mongo2 -p 27019:27017 -d mongo --enableMajorityReadConcern --replSet rs001

docker run --net mynet123 --ip 172.18.0.13 --name mongo3 -p 27020:27017 -d mongo --enableMajorityReadConcern --replSet rs001

mongo --port 27018 --eval 'rs.initiate({_id: "rs001",version: 1,members: [{_id: 0,host: "172.18.0.11:27017"}]})'

mongo --port 27018 --eval 'rs.add("172.18.0.12:27017")'
mongo --port 27018 --eval 'rs.add("172.18.0.13:27017")'

mongo --port 27018 --eval 'db.getMongo().setReadPref("primaryPreferred")'