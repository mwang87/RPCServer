import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

def test_run():
    print 'RUNNING JOB'
    return "MING"

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()