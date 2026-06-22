from fastapi import FastAPI
from .router import MCPRouter
from .transformer import transform
from .event_bus import create_event

app = FastAPI()
router = MCPRouter()


@app.post("/ingest/{source}")
def ingest(source: str, payload: dict):
    parsed = router.route(source, payload)
    transformed = transform(source, parsed)
    event = create_event(source, transformed)

    return event
