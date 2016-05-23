import pika
import json
import pymongo
import ConfigParser
from Logger import Logger

# pika settings
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.exchange_declare(exchange='tornado', type='topic', durable=True)

channel.queue_declare(queue="creation", durable=True)
channel.queue_declare(queue="reading", durable=True)

channel.basic_qos(prefetch_count=1)  # count messages to a worker at a time

# logger
logger_cc = Logger('callback_creation').get()
logger_cr = Logger('callback_reading').get()


# replica connection string from mongo_conf.ini
cfg_parser = ConfigParser.ConfigParser()
cfg_parser.read('mongo_conf.ini')

cfg = ''
for _ in cfg_parser.sections():
    cfg = cfg + cfg_parser.get(_, 'ip') + ':'
    cfg = cfg + cfg_parser.get(_, 'port') + ','
cfg = 'mongodb://' + cfg[:-1] + '/replicaSet=rs001/?localThresholdMS=15'

# pymongo settings
client = pymongo.MongoClient(cfg, readPreference='primaryPreferred')
db = client["local"]["test"]


def callback_creation(ch, method, properties, body):
    body = json.loads(body)
    logger_cc.info('get {0}.'.format(body))
    if len(body["id"]) == 0:
        answer = {"status": 400, "response": "Id was missing"}
    else:
        try:
            if db.find_one({"id": body["id"]}) is None:
                db.insert_one(body)
            else:
                db.update_one({"id": body["id"]},
                              {"$set": {"content": body["content"]}})
            answer = {"status": 200, "response": "Message was added"}
        except (pymongo.errors.ServerSelectionTimeoutError,
                pymongo.errors.NetworkTimeout,
                pymongo.errors.AutoReconnect):
            answer = {"status": 500, "response": "Something has gone wrong"}
    logger_cc.info('return {0}.'.format(answer))
    channel.basic_publish(exchange="tornado",
                          routing_key="answer",
                          body=json.dumps(answer),
                          properties=pika.BasicProperties(delivery_mode=2,))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_reading(ch, method, properties, body):
    body, err = json.loads(body), 0
    logger_cr.info('get {0}.'.format(body))
    if len(body["id"]) == 0:
        answer = {"status": 400, "response": "Id was missing"}
    else:
        try:
            answer = db.find_one(body)
        except (pymongo.errors.ServerSelectionTimeoutError,
                pymongo.errors.NetworkTimeout,
                pymongo.errors.AutoReconnect):
            answer = {"status": 500, "response": "Something has gone wrong"}
            err = 1
    if answer is None:
        db.insert_one({"id": body["id"], "content": ""})
        answer = {"status": 200, "content": ""}
    elif err == 0:
        answer = {"status": 200, "content": answer["content"]}
    logger_cr.info('return {0}.'.format(answer))
    channel.basic_publish(exchange="tornado",
                          routing_key="answer",
                          body=json.dumps(answer),
                          properties=pika.BasicProperties(delivery_mode=2,))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(callback_creation, queue="creation")
channel.basic_consume(callback_reading, queue="reading")


# TEST will be removed soon
logger_ct = Logger('callback_test').get()
channel.queue_declare(queue="answer", durable=True)


def callback_test(ch, method, properties, body):
    body = json.loads(body)
    logger_ct.info('return {0}.'.format(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(callback_test, queue="answer")
# TEST will be removed soon

channel.start_consuming()
