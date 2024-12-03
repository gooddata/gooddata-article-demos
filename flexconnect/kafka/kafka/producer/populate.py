# (C) 2024 GoodData Corporation
import json
import logging
import os
import random
import time
from datetime import datetime

from faker import Faker

from kafka import KafkaProducer

fake = Faker()

count = 1000
event_types = ["START", "END", "LEAD"]
flush_batch = 10000

log_handler = logging.StreamHandler()
logger = logging.getLogger()
logger.addHandler(log_handler)
logger.setLevel(os.environ.get("LOGLEVEL", "INFO"))


def get_data():
    return {
        "transaction_id": fake.uuid4(),
        "account_id": f"acc_{fake.random_int(min=1, max=10)}",
        "amount": str(round(random.uniform(10.0, 1000.0), 2)),
        "currency": fake.currency_code(),
        "timestamp": str(datetime.now().isoformat()),
        "transaction_type": random.choice(["deposit", "withdrawal", "transfer"]),
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers="kafka:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    for j in range(1000):
        logger.info(f"Populating {count} messages iteration={j} ...")
        for i in range(count):
            producer.send("test", get_data())
            if (i % flush_batch) == 0:
                logger.info("Flushing messages ... ")
                producer.flush(5)
        time.sleep(1)
    logger.info("Flushing rest of messages ... ")
    producer.flush(5)


if __name__ == "__main__":
    main()
