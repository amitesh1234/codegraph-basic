from app.db import run_query
from app.parser import parse_repo

def index_repo(repo_path):
    functions, edges = parse_repo(repo_path)

    # 1) Write function nodes (idempotent)
    run_query(
        """
        UNWIND $rows AS row
        MERGE (f:Function {id: row.id})
        SET f.name = row.name, f.file = row.file, f.line = row.line
        """,
        {"rows": functions},
    )

    # 2) Write CALLS edges (nodes must exist first)
    edge_rows = [{"caller": a, "callee": b} for a, b in edges]
    run_query(
        """
        UNWIND $rows AS row
        MATCH (a:Function {id: row.caller})
        MATCH (b:Function {id: row.callee})
        MERGE (a)-[:CALLS]->(b)
        """,
        {"rows": edge_rows},
    )

    return {
        "functions_indexed": len(functions),
        "call_edges_indexed": len(edges),
    }
