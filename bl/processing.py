import pika
import json
import pymongo
import time
import ConfigParser
import sys
from Logger import Logger


def mongo_connection(database, collection):
    cfg_parser = ConfigParser.ConfigParser()
    cfg_parser.read(sys.argv[1])
    mongo_nodes = zip(cfg_parser.get('mongocluster', 'hosts').split(' '),
                      cfg_parser.get('mongocluster', 'ports').split(' '))

    cfg = ''
    for _ in mongo_nodes:
        cfg = cfg + _[0] + ':'
        cfg = cfg + _[1] + ','

    cfg = 'mongodb://' + cfg[:-1] + '/replicaSet=rs001/?localThresholdMS=15'

    client = pymongo.MongoClient(cfg, readPreference='primaryPreferred')
    return client[database][collection]


def rabbit_connection():
    cfg_parser = ConfigParser.ConfigParser()
    cfg_parser.read(sys.argv[1])
    rabbit_nodes = zip(cfg_parser.get('rabbitmq', 'hosts').split(' '),
                       cfg_parser.get('rabbitmq', 'ports').split(' '))
    try:
        global r_numb
        r_numb += 1
        r_numb %= 3

        logger_rb.info('try to use port {0}.'.format(rabbit_nodes[r_numb][1]))

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(rabbit_nodes[r_numb][0],
                                      port=int(rabbit_nodes[r_numb][1])))

        logger_rb.info('using port {0}.'.format(rabbit_nodes[r_numb][1]))
        return connection
    except (pika.exceptions.IncompatibleProtocolError,
            pika.exceptions.ConnectionClosed):
        time.sleep(5)
        rabbit_connection()


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


if __name__ == '__main__':
    r_numb = 2

    # loggers
    logger_cc = Logger('callback_creation').get()
    logger_cr = Logger('callback_reading').get()
    logger_rb = Logger('rabbit port using').get()

    db = mongo_connection("local", "test")

    connection = rabbit_connection()
    channel = connection.channel()
    channel.exchange_declare(exchange='tornado', type='direct', durable=True)

    channel.queue_declare(queue="creation", durable=True)
    channel.queue_declare(queue="reading", durable=True)

    channel.basic_qos(prefetch_count=1)  # count messages to a worker

    channel.basic_consume(callback_creation, queue="creation")
    channel.basic_consume(callback_reading, queue="reading")

    channel.start_consuming()
