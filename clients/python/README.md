# py-files-cli

Console client for upload and download (MVP).

Install:

```bash
cd clients/python
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Check a remote server before uploading:

```bash
pyfiles --base-url http://127.0.0.1:8000 status
```

Log in and save local CLI config:

```bash
pyfiles --base-url http://127.0.0.1:8000 login --login alice --password secretpw
```

Upload a local file using the saved server URL and token:

```bash
pyfiles upload ./example.bin
```

You can also override the saved server URL for a single upload:

```bash
pyfiles --base-url http://127.0.0.1:8000 upload ./example.bin
```
