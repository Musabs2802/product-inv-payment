from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse
from redis_om import get_redis_connection, HashModel
from redis_om.model.model import NotFoundError
from starlette.requests import Request
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# This will be a different database
redis = get_redis_connection(
    host="redis-14871.c264.ap-south-1-1.ec2.cloud.redislabs.com",
    port=14871,
    password="k9VUqIKIPHLP1rm3qSxQ0MS4VJldlE1i",
    decode_responses=True,
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # Status: pending, completed, refunded

    class Meta:
        database = redis


@app.get("/")
def root():
    return {"message": "Hello World !"}


@app.get("/orders")
async def get_all():
    return Order.all_pks()


@app.get("/orders/{pk}")
async def get_order(pk: str):
    return Order.get(pk)


@app.post("/orders")
async def create(request: Request, background_task: BackgroundTasks):
    body = await request.json()

    req = requests.get("http://localhost:8000/products/{}".format(body["id"]))
    product = req.json()

    order = Order(
        product_id=body["id"],
        price=product["price"],
        fee=0.2 * product["price"],
        total=1.2 * product["price"],
        quantity=body["quantity"],
        status="pending",
    )
    order.save()

    background_task.add_task(order_completed, order)

    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()

    redis.xadd("order_completed", order.dict(), "*")
    
