import pika
import json
import pymongo

#pika settings
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

channel.queue_declare(queue="creation", durable=True)
channel.queue_declare(queue="reading", durable=True)

###TEST
channel.queue_declare(queue="answer", durable=True)
###TEST

channel.basic_qos(prefetch_count=1) ### count messages to a worker at a time

#pymongo settings
client = pymongo.MongoClient("172.17.0.3", 27017)
db = client["local"]["test"]


def callback_creation(ch, method, properties, body):
    body = json.loads(body)
    if len(body["id"]) == 0 or len(body["message"]) == 0:
        answer = {"status": 400, "message": "Enter id or/and message"}
    else:
        try:
            if db.find_one({"id": body["id"]}) is None:
                db.insert_one(body)
            else:
                db.update_one({"id": body["id"]}, {"$set":
                              {"message": body["message"]}})
            answer = {"status": 200, "message": "Message created or modified"}
        except pymongo.errors.ServerSelectionTimeoutError, \
                pymongo.errors.NetworkTimeout:
            answer = {"status": 400, "message": "Something gone wrong"}
    channel.basic_publish(exchange="",
                          routing_key="answer",
                          body=json.dumps(answer),
                          properties=pika.BasicProperties(delivery_mode=2,))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def callback_reading(ch, method, properties, body):
    body = json.loads(body)
    if len(body["id"]) == 0:
        answer = {"status": 400, "message": "Enter id"}
    else:
        try:
            answer = db.find_one(body)
        except pymongo.errors.ServerSelectionTimeoutError, \
                pymongo.errors.NetworkTimeout:
            answer = {"status": 400, "message": "Something gone wrong"}
    if answer is None:
        answer = {"status": 400, "message": "Message not exist"}
    else:
        answer = answer["message"]
    channel.basic_publish(exchange="",
                          routing_key="answer",
                          body=json.dumps(answer),
                          properties=pika.BasicProperties(delivery_mode=2,))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(callback_creation, queue="creation")
channel.basic_consume(callback_reading, queue="reading")

###TEST
def callback_test(ch, method, properties, body):
    body = json.loads(body)
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
channel.basic_consume(callback_test, queue="answer")
###TEST

channel.start_consuming()
