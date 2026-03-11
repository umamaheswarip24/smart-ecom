from flask import Flask, request, jsonify

import pika
import json
import os

app = Flask(__name__)

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')



def publish_event(event_data):
    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        ch = conn.channel()
        ch.queue_declare(queue='events', durable=True)
        ch.basic_publish(
            exchange='',
            routing_key='events',
            body=json.dumps(event_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        conn.close()
        return True
    except Exception as e:
        print(f"RabbitMQ error: {e}")
        return False

@app.post('/pay')
def pay():
    data = request.get_json(force=True)
    amount = data.get('amount', 0)
    method = data.get('method', 'card')
    discount_code = data.get('discount_code', '')

    # Apply discount
    discount = 0.0
    if discount_code == 'NEWYEAR':
        discount = 0.20

    final_amount = round(amount * (1 - discount), 2)

    # Publish to RabbitMQ
    event = {
        "event": "payment_processed",
        "original_amount": amount,
        "discount_code": discount_code,
        "discount": discount,
        "final_amount": final_amount,
        "method": method
    }
    published = publish_event(event)

    return jsonify({
        "status": "success",
        "original_amount": amount,
        "discount": f"{int(discount * 100)}%",
        "final_amount": final_amount,
        "method": method,
        "event_published": published
    })
app.run(host='0.0.0.0', port=3002)
