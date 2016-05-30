from server.Session import Session
import time
import random

startup_nodes = [{'host': '172.17.0.2', 'port': 7000},
                 {'host': '172.17.0.2', 'port': 7001},
                 {'host': '172.17.0.2', 'port': 7002}]
session_store = Session(startup_nodes=startup_nodes)

i = 0
while True:
    time.sleep(random.randint(1, 10))
    print("Starting...")
    uui = "test_info" + str(i)
    i += 1
    res_get = session_store.get(uui)
    if res_get:
        print("GET: %s" % res_get)
    else:
        print("SET")
        session_store.set(uui)
    print("Sleeping...")
    time.sleep(10)
