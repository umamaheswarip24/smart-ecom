import pika
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
ch = conn.channel()
ch.queue_declare(queue='events', durable=True)
ch.basic_publish(exchange='', routing_key='events', body='payment_processed')
conn.close()