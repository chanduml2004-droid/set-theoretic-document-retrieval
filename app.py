"""Set-Theoretic Document Retrieval System - standard-library web application."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import json, re, html

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "documents.json"
STOP_WORDS = {"a", "an", "the", "is", "are", "of", "and", "or", "in", "on", "to", "for", "with", "by", "this", "that"}

def load_documents():
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def tokenize(text):
    return [w.lower() for w in re.findall(r"[A-Za-z0-9]+", text) if w.lower() not in STOP_WORDS]

def build_index(documents):
    """Return term -> set(document IDs) inverted index."""
    index = {}
    for doc in documents:
        for term in set(tokenize(doc["title"] + " " + doc["content"])):
            index.setdefault(term, set()).add(doc["id"])
    return index

def evaluate_query(query, index, all_ids):
    """Evaluate a Boolean query with AND, OR, NOT and parentheses.

    Grammar: expression := or_expr; OR has lower precedence than AND;
    NOT is unary; parentheses group expressions. Implicit AND is supported.
    """
    tokens = re.findall(r"\(|\)|[A-Za-z0-9]+", query)
    if not tokens:
        raise ValueError("Enter a search term or Boolean expression.")

    normalized = []
    for t in tokens:
        u = t.upper()
        normalized.append(u if u in {"AND", "OR", "NOT"} else t.lower())

    # Insert implicit AND between adjacent operands / closing and opening groups.
    expanded = []
    for i, tok in enumerate(normalized):
        if i:
            prev = normalized[i-1]
            if (prev not in {"AND", "OR", "NOT", "("} and tok not in {"AND", "OR", ")"}) or (prev == ")" and tok not in {"AND", "OR", ")"}):
                expanded.append("AND")
        expanded.append(tok)

    pos = 0
    def peek():
        return expanded[pos] if pos < len(expanded) else None
    def parse_primary():
        nonlocal pos
        tok = peek()
        if tok == "NOT":
            pos += 1
            return all_ids - parse_primary()
        if tok == "(":
            pos += 1
            result = parse_or()
            if peek() != ")":
                raise ValueError("Missing closing parenthesis.")
            pos += 1
            return result
        if tok is None or tok in {"AND", "OR", ")"}:
            raise ValueError("Expected a search term.")
        pos += 1
        return set(index.get(tok, set()))
    def parse_and():
        nonlocal pos
        result = parse_primary()
        while peek() == "AND":
            pos += 1
            result &= parse_primary()
        return result
    def parse_or():
        nonlocal pos
        result = parse_and()
        while peek() == "OR":
            pos += 1
            result |= parse_and()
        return result

    result = parse_or()
    if pos != len(expanded):
        raise ValueError(f"Unexpected token: {expanded[pos]}")
    return result

def search(query):
    docs = load_documents()
    index = build_index(docs)
    ids = {d["id"] for d in docs}
    matched = evaluate_query(query, index, ids)
    return [d for d in docs if d["id"] in matched], len(index)

class Handler(BaseHTTPRequestHandler):
    def send(self, body, status=200, content_type="text/html; charset=utf-8"):
        raw = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/documents":
            self.send(json.dumps(load_documents(), ensure_ascii=False), content_type="application/json; charset=utf-8")
            return
        if path == "/":
            page = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
            self.send(page)
            return
        if path.startswith("/static/"):
            asset = ROOT / path.lstrip("/")
            if asset.exists() and asset.is_file():
                ctype = "text/css; charset=utf-8" if asset.suffix == ".css" else "application/javascript; charset=utf-8"
                self.send(asset.read_text(encoding="utf-8"), content_type=ctype)
                return
        self.send("Not found", 404, "text/plain; charset=utf-8")

    def do_POST(self):
        if urlparse(self.path).path != "/api/search":
            self.send('{"error":"Not found"}', 404, "application/json")
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            query = str(payload.get("query", "")).strip()
            results, vocab_size = search(query)
            response = {"query": query, "count": len(results), "vocabulary_size": vocab_size, "results": results}
            self.send(json.dumps(response, ensure_ascii=False), content_type="application/json; charset=utf-8")
        except (ValueError, json.JSONDecodeError) as exc:
            self.send(json.dumps({"error": str(exc)}), 400, "application/json; charset=utf-8")

    def log_message(self, fmt, *args):
        print("[server] " + fmt % args)

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Set-Theoretic Document Retrieval System")
    print("Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
        server.server_close()
