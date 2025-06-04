import redis
import os
import json

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url, decode_responses=True)

def set_temp_user(user_id, data, ttl=1800):
    redis_client.setex(f"temp_user:{user_id}", ttl, json.dumps(data))

def get_temp_user(user_id):
    data = redis_client.get(f"temp_user:{user_id}")
    return json.loads(data) if data else None

def del_temp_user(user_id):
    redis_client.delete(f"temp_user:{user_id}")

def set_manual_pending(code, data, ttl=3600):
    redis_client.setex(f"manual_code:{code}", ttl, json.dumps(data))

def get_manual_pending(code):
    data = redis_client.get(f"manual_code:{code}")
    return json.loads(data) if data else None

def del_manual_pending(code):
    redis_client.delete(f"manual_code:{code}")
