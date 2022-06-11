from collections import Counter
from typing import Mapping

from fastapi import FastAPI

app = FastAPI()
counter = Counter()


@app.get("/{counter_name}")
def read_counter(counter_name: str) -> Mapping:
    return {counter_name: counter[counter_name]}


@app.get("/{counter_name}/inc")
def increase_counter(counter_name: str) -> Mapping:
    counter.update([counter_name])
    return {counter_name: counter[counter_name]}


@app.get("/")
def get_all() -> Mapping:
    return dict(counter)
