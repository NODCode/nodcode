##Install Redis

	wget http://download.redis.io/redis-stable.tar.gz
	tar xvzf redis-stable.tar.gz
	cd redis-stable
	make
	sudo make install

##Configure the replication

	git clone https://github.com/ServiceStack/redis-config.git
	cd redis-config\sentinel3\linux

#Start 1x master, 2x slaves, 3x Sentinel redis-servers:

	./start-all.sh

##Wait a few seconds before hitting return until you see +slave and +sentinel log entries in the console output. Then press "Enter".

## Servers are ready to work!

#Stop all:

	./stop-all.sh

##If you have problems with permissions, try: 
#	chmod a=rx start-all.sh
#	chmod a=rx stop-all.sh



	

