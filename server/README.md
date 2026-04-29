# py-files-server

FastAPI service for authenticated file upload and download (MVP).

Install (development, with test tools):

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Run (after implementation in later phases):

```bash
uvicorn py_files_server.main:app --reload
```
