from flask import Flask, request, jsonify
from pymongo import MongoClient
from kafka import KafkaConsumer
from threading import Thread
import os

app = Flask(__name__)


# MongoDB configuration
MONGO_USERNAME = os.getenv("MONGODB_USERNAME")
MONGO_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{os.getenv("MONGODB_HOST")}/'
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = 'items'

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Kafka configuration
KAFKA_SERVERS = os.getenv("KAFKA_HOST")
KAFKA_TOPIC = 'item_purchases'

# Connect to Kafka
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_SERVERS, group_id='my_consumer_group')

# Function to consume Kafka messages and add purchases to MongoDB
def consume_and_add_purchases():
    for message in consumer:
        data = message.value.decode('utf-8').split(',')
        user_id = data[0]
        item_id = data[1]
        add_purchase(user_id, item_id)

# Function to add a purchase to MongoDB
def add_purchase(user_id, item_id):
    purchase = {
        'user_id': user_id,
        'item_id': item_id
    }
    collection.insert_one(purchase)

# Route to get all purchased items
@app.route('/purchased_items', methods=['GET'])
def get_purchased_items():
    purchased_items = list(collection.find({}, {'_id': False}))
    print(purchased_items)
    return jsonify(purchased_items)

# Start Kafka consumer thread
kafka_consumer_thread = Thread(target=consume_and_add_purchases)
kafka_consumer_thread.daemon = True
kafka_consumer_thread.start()
if __name__ == '__main__':

    # Run Flask app
    app.run(debug=True)
