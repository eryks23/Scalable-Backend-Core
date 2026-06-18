# redis_patterns.py

> Practical Redis design patterns in Python — rate limiting and cache-aside, runnable with zero infrastructure.

## Description

`redis_patterns.py` is a focused reference implementation of two foundational Redis patterns: **rate limiting** and **cache-aside (lazy loading)**. It uses `fakeredis` for fully local execution — no Redis server required. The code is written to be readable, copy-paste-friendly, and trivially swappable for a production `redis.Redis` client.

Part of the [Scalable-Backend-Core](https://github.com/eryks23/Scalable-Backend-Core) repository.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Running the Demo](#running-the-demo)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Per-user rate limiting** — enforces a request cap within a rolling time window using atomic Redis `INCR` + `EXPIRE`
- **Cache-aside (lazy loading)** — checks cache on read, populates on miss, auto-expires stale data; includes a simulated DB fetch
- **No infrastructure required** — `fakeredis` replaces a live Redis instance for local development and testing
- **Drop-in production upgrade** — swap `FakeStrictRedis` for `redis.StrictRedis` with a single line change

---

## Tech Stack

| Component  | Role                            |
|------------|---------------------------------|
| Python     | Runtime language                |
| fakeredis  | In-memory Redis mock (dev/test) |

---

## Requirements

- Python **3.8+**
- pip

---

## Installation

```bash
# Clone the repository
git clone https://github.com/eryks23/Scalable-Backend-Core.git
cd Scalable-Backend-Core

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Run the built-in demo

```bash
python redis_patterns.py
```

Expected output:

```
=== TEST 1: Rate Limiter ===
Attempt 1: OK
Attempt 2: OK
Attempt 3: OK
Attempt 4: BLOCKED
Attempt 5: BLOCKED

=== TEST 2: Cache Aside ===
--- [DB] Fetching user user_42 from database... ---
Call 1: {'name': 'Adam', 'role': 'intern', 'tasks_done': '5', 'status': 'fresh_from_db'}
Call 2: {'name': 'Adam', 'role': 'intern', 'tasks_done': '5', 'status': 'cached'}
```

### Import into your own code

```python
from redis_patterns import check_rate_limit, get_user_data

# Rate limiting
if check_rate_limit("user_42"):
    print("Request allowed")
else:
    print("Too many requests — try again later")

# Cache-aside
profile = get_user_data("user_42")
print(profile["name"])    # Adam
print(profile["status"])  # fresh_from_db (first call) / cached (subsequent)
```

### Switching to a real Redis instance

Replace the client at the top of `redis_patterns.py`:

```python
# Development — current default
import fakeredis
r = fakeredis.FakeStrictRedis(decode_responses=True)

# Production
import redis
r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
```

---

## API Reference

### `check_rate_limit(user_id: str) -> bool`

Determines whether a user is within the allowed request limit for the current time window.

| Parameter | Type  | Description                          |
|-----------|-------|--------------------------------------|
| `user_id` | `str` | Unique identifier for the user or client |

**Returns:** `True` if the request is permitted; `False` if the limit has been exceeded.

**Behaviour:**
- Limit: **3 requests per 10-second window**
- Redis key: `rate_limit:{user_id}`
- Counter incremented atomically with `INCR`; TTL of 10 s set on the first call only
- TTL resets naturally — no manual cleanup required

```python
for i in range(5):
    result = check_rate_limit("user_42")
    # i=0,1,2 → True | i=3,4 → False
```

---

### `get_user_data(user_id: str) -> dict`

Fetches a user profile using the cache-aside (lazy loading) pattern.

| Parameter | Type  | Description                   |
|-----------|-------|-------------------------------|
| `user_id` | `str` | Unique identifier for the user |

**Returns:** A `dict` containing user fields plus a diagnostic `"status"` key:

| `"status"` value    | Meaning                                          |
|---------------------|--------------------------------------------------|
| `"fresh_from_db"`   | Cache miss — data fetched from DB and cached     |
| `"cached"`          | Cache hit — data returned directly from Redis    |

**Behaviour:**
- Redis key: `user:profile:{user_id}` (stored as a Redis hash)
- Cache TTL: **30 seconds**
- On a cache miss, simulates a DB query, writes the result to Redis, and sets the TTL

```python
first  = get_user_data("user_42")  # triggers DB fetch, writes to cache
second = get_user_data("user_42")  # served from cache, no DB call
```

---

## Project Structure

```
Scalable-Backend-Core/
├── redis_patterns.py   # Rate limiter + cache-aside implementations and demo
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
└── README.md
```

---

## Running the Demo

The `__main__` block runs two self-contained scenarios end-to-end — no setup required.

**Test 1 — Rate Limiter**
Fires 5 consecutive requests for `user_42`. Requests 1–3 are allowed; 4 and 5 are blocked because the counter exceeds the limit of 3 within the 10-second window.

**Test 2 — Cache Aside**
Calls `get_user_data` twice in sequence. The first call logs a simulated database fetch and writes the result to the cache. The second call reads silently from Redis and returns `status: cached`.

```bash
python redis_patterns.py
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-redis-pattern`
3. Commit your changes with a clear message: `git commit -m "feat: add pub/sub pattern example"`
4. Push the branch: `git push origin feature/new-redis-pattern`
5. Open a Pull Request against `main`

**Guidelines:**
- Keep each new pattern self-contained in its own function
- Add a corresponding demo block in the `__main__` section
- Prefer `fakeredis` for any new tests — no live Redis dependency
- Follow existing naming conventions (`snake_case`, descriptive function names)

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Author

**eryks23** — [github.com/eryks23](https://github.com/eryks23)
