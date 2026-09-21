"""Self-hosted laya (ModernBERT-large typed decisions), same /decide contract as open-jev."""
import json
import threading
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
agent = None
load_seconds = None


def _load():
    global agent, load_seconds
    t0 = time.time()
    import laya

    a = laya.load("convaiinnovations/laya", subfolder="typed-decisions")
    load_seconds = round(time.time() - t0, 1)
    agent = a
    print(f"laya loaded in {load_seconds}s")


threading.Thread(target=_load, daemon=True).start()


class Req(BaseModel):
    state: str
    questions: list


def to_laya(q, idx):
    name = f"q{idx}"
    t = q.get("type")
    if t == "noul":
        return name, {"type": "noul", "instructions": q["instructions"]}
    if t == "choice":
        return name, {"type": "choice", "instructions": q["instructions"],
                      "criteria": {o: o for o in q["options"]}}
    if t == "score":
        return name, {"type": "score", "instructions": q["instructions"], "criteria": list(q["options"])}
    raise ValueError(f"unknown question type {t}")


def jsonable(x):
    return json.loads(json.dumps(x, default=lambda o: float(o) if hasattr(o, "__float__") else str(o)))


@app.get("/healthz")
def healthz():
    return {"ok": True, "model_loaded": agent is not None, "load_seconds": load_seconds, "model": "laya-typed-decisions (ModernBERT-large, 1024 ctx)"}


@app.post("/decide")
def decide(r: Req):
    if agent is None:
        return JSONResponse({"error": "model still loading"}, status_code=503)
    t0 = time.time()
    qmap = dict(to_laya(q, i) for i, q in enumerate(r.questions))
    result = agent.predict(r.state, qmap)
    answers = [jsonable(result["answers"][f"q{i}"]) for i in range(len(r.questions))]
    ms = round((time.time() - t0) * 1000, 1)
    return {"answers": answers, "latency_ms": ms}
