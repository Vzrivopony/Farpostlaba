import random
import string
import time
import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)

while True:
    message = "".join(
        random.choices(string.ascii_letters + string.digits, k=10)
    )
    r.lpush("messages", json.dumps({"message": message}))
    print(f"Sent: {message}")
    time.sleep(60)