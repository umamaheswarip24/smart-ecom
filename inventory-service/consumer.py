import pika
import json
import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'localhost')

def on_msg(ch, method, props, body):
    try:
        event = json.loads(body.decode())
        print(f"Event received: {event}")
    except Exception as e:
        print(f"Error: {e}")

conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
ch = conn.channel()
ch.queue_declare(queue='events', durable=True)
ch.basic_consume(queue='events', on_message_callback=on_msg, auto_ack=True)
print("Waiting for events...")
ch.start_consuming()