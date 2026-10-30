# Set-Theoretic Document Retrieval System

A complete, beginner-friendly mini project demonstrating Boolean document retrieval with set operations. It uses only Python's standard library, so no third-party packages are required.

## Features
- Inverted index: each normalized term maps to a set of document IDs.
- Boolean operators: `AND`, `OR`, `NOT`, and parentheses.
- Correct precedence: `NOT` > `AND` > `OR`.
- Implicit AND: `python data` is treated as `python AND data`.
- Browser-based search interface with example queries and matching document cards.
- Ten editable sample documents in `data/documents.json`.
- JSON API endpoint for search results.

## Requirements
- Python 3.9 or newer
- Any modern web browser

## Run the project
1. Extract the ZIP file.
2. Open a terminal in the extracted `set_theoretic_document_retrieval` folder.
3. Run:

   ```bash
   python app.py
   ```

4. Open **http://127.0.0.1:8000** in your browser.
5. Press `Ctrl+C` in the terminal to stop the server.

No `pip install` step is needed.

## Example queries

| Query | Meaning |
|---|---|
| `python AND data` | Documents containing both terms |
| `machine OR learning` | Documents containing either term |
| `NOT database` | All documents that do not contain database |
| `(python OR java) AND NOT web` | Python or Java documents, excluding documents containing web |
| `information retrieval` | Implicit AND: both terms must occur |

## How the algorithm works
1. Read all documents from the JSON collection.
2. Tokenize title and body text, convert terms to lowercase, and remove common stop words.
3. Build an inverted index: `term -> set(document IDs)`.
4. Let `U` be the set of all document IDs.
5. Evaluate a query:
   - `A AND B` = intersection, `A ∩ B`
   - `A OR B` = union, `A ∪ B`
   - `NOT A` = complement relative to the collection, `U − A`
6. Return documents whose IDs are in the resulting set.

## Project structure
```text
set_theoretic_document_retrieval/
├── app.py                  # HTTP server, indexer and Boolean query parser
├── data/
│   └── documents.json      # Sample document collection
├── static/
│   ├── app.js              # Search interface behavior
│   └── style.css           # UI styling
├── templates/
│   └── index.html          # Main web page
├── tests/
│   └── test_retrieval.py   # Unit tests
├── requirements.txt
├── run.bat                 # Windows launcher
├── run.sh                  # macOS/Linux launcher
└── README.md
```

## Run tests
From the project folder:

```bash
python -m unittest discover -s tests -v
```

## API
`POST /api/search` with JSON body:

```json
{"query": "python AND data"}
```

The response includes the original query, number of matching documents, indexed vocabulary size, and matching document objects.

## Limitations / possible extensions
This educational implementation uses simple tokenization and exact term matching; it does not perform stemming, ranking, phrase search, fuzzy matching, or persistent user uploads. You can extend it with TF-IDF ranking, PDF/text ingestion, or a database.
