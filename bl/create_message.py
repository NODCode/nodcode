import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='creation', durable=True)

message = {'id': '111',
           'message': 'hallo_world1'}

message_d = json.dumps(message)

channel.basic_publish(exchange='',
                      routing_key='creation',
                      body=message_d,
                      properties=pika.BasicProperties(delivery_mode=2,))

print("Sent", message)


connection.close()
