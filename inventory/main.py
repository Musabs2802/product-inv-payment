from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from redis_om import get_redis_connection, HashModel
from redis_om.model.model import NotFoundError

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


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/")
def root():
    return {"message": "Hello World !"}


@app.get("/products")
def all_products():
    return [format(p) for p in Product.all_pks()]


@app.get("/products/{pk}")
def get(pk: str):
    try:
        return Product.get(pk)
    except NotFoundError:
        return JSONResponse(status_code=404, content={"message": "Not found !"})


@app.post("/products")
def create(product: Product):
    return product.save()


@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.delete(pk)


def format(pk: str):
    return Product.get(pk)
