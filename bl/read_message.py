import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='reading', durable=True)

message = {'id': '111'}

message_d = json.dumps(message)

channel.basic_publish(exchange='tornado',
                      routing_key='reading',
                      body=message_d,
                      properties=pika.BasicProperties(delivery_mode=2,))

print("Sent", message)


connection.close()
