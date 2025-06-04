from extensions import redis_client
import json

def set_temp_user(user_id, data, expire=1800):
    redis_client.set(f"temp_user:{user_id}", json.dumps(data), ex=expire)
def get_temp_user(user_id):
    val = redis_client.get(f"temp_user:{user_id}")
    return json.loads(val) if val else None
def del_temp_user(user_id):
    redis_client.delete(f"temp_user:{user_id}")

def set_manual_pending(code, data, expire=1800):
    redis_client.set(f"manual_pending:{code}", json.dumps(data), ex=expire)
def get_manual_pending(code):
    val = redis_client.get(f"manual_pending:{code}")
    return json.loads(val) if val else None
def del_manual_pending(code):
    redis_client.delete(f"manual_pending:{code}")
