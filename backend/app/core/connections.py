from elasticsearch import Elasticsearch
import redis
import psycopg


# Elasticsearch
es = Elasticsearch("http://localhost:9200")


# Redis 
# this is where we are connecting with redis 
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


# PostgreSQL
def get_pg_connection():
    return psycopg.connect(
        host="localhost",
        port=5433,
        dbname="cyberpulse",
        user="cyberpulse",
        password="cyberpulse_dev",
    )