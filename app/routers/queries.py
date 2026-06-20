from fastapi import APIRouter
from app.db import run_query
from app.memory import log_run

router = APIRouter(prefix="/query", tags=["queries"])

@router.get("/who-calls")
def who_calls(name: str):
    rows = run_query(
        "MATCH (c:Function)-[:CALLS]->(:Function {name: $name}) "
        "RETURN DISTINCT c.name AS name, c.file AS file",
        {"name": name},
    )
    log_run("who-calls", target=name, result_count=len(rows))
    return {"target": name, "callers": rows}

@router.get("/impact")
def impact(name: str, depth: int = 3):
    depth = max(1, min(depth, 5))                      # clamp; also keeps it an int
    cypher = (
        "MATCH (c:Function)-[:CALLS*1.." + str(depth) + "]->"
        "(:Function {name: $name}) "
        "RETURN DISTINCT c.name AS name, c.file AS file"
    )
    rows = run_query(cypher, {"name": name})
    log_run("impact", target=name, result_count=len(rows))
    return {"target": name, "depth": depth,
            "impacted_by_change": rows}
    
@router.get("/depends-on")
def depends_on(name: str, depth: int = 3):
    depth = max(1, min(depth, 5))
    cypher = (
        "MATCH path = (:Function {name: $name})-[:CALLS*1.." + str(depth) + "]->"
        "(d:Function) "
        "WITH d, min(length(path)) AS hop "
        "RETURN d.name AS name, d.file AS file, hop "
        "ORDER BY hop, name"
    )
    rows = run_query(cypher, {"name": name})
    log_run("depends-on", target=name, result_count=len(rows))
    return {"target": name, "depth": depth,
            "depends_on": rows}