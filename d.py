import fakeredis

r = fakeredis.FakeStrictRedis(decode_responses=True)


def check_rate_limit(user_id):
    key = f"rate_limit:{user_id}"
    
    current_count = r.incr(key)
    
    if current_count == 1:
        r.expire(key, 10)
        
    return current_count <= 3


def get_user_data(user_id):
    cache_key = f"user:profile:{user_id}"
    cached_data = r.hgetall(cache_key)
    
    if cached_data:
        cached_data["status"] = "cached"
        return cached_data

    print(f"--- [DB] Fetching user {user_id} from database... ---")
    db_data = {"name": "Adam", "role": "intern", "tasks_done": "5"}
    
    r.hset(cache_key, mapping=db_data)
    r.expire(cache_key, 30)
    
    db_data["status"] = "fresh_from_db"
    return db_data


if __name__ == "__main__":
    print("=== TEST 1: Rate Limiter ===")
    user_id = "user_42"

    for i in range(1, 6):
        allowed = check_rate_limit(user_id)
        print(f"Attempt {i}: {'OK' if allowed else 'BLOCKED'}")

    print("\n=== TEST 2: Cache Aside ===")
    print("Call 1:", get_user_data(user_id))
    print("Call 2:", get_user_data(user_id))