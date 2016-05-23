##Go to directory with servers	
	cd redis-stable/redis-config/sentinel3/linux
	
##To stop server on port 6380:
	sudo redis-cli -p 26380 SHUTDOWN NOSAVE
	sudo redis-cli -p 6380 SHUTDOWN NOSAVE

##To start server on port 6380:
	sudo redis-server server-6380/redis.conf & redis-sentinel server-6380/sentinel.conf &


##To stop server on port 6381:
	sudo redis-cli -p 26381 SHUTDOWN NOSAVE
	sudo redis-cli -p 6381 SHUTDOWN NOSAVE

##To start server on port 6381:
	sudo redis-server server-6381/redis.conf & redis-sentinel server-6381/sentinel.conf &


##To stop server on port 6382:
	sudo redis-cli -p 26382 SHUTDOWN NOSAVE
	sudo redis-cli -p 6382 SHUTDOWN NOSAVE

##To start server on port 6382:
	sudo redis-server server-6382/redis.conf & redis-sentinel server-6382/sentinel.conf &

##After master on port 6380 is stopped, slave on port 6381 (if it is reachable) became a master. Like in mongo.

