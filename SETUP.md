# Development Setup

## Create virtual environment

```bash
python3 -m venv venv
```

## Activate

```bash
source venv/bin/activate
```

## Install Pinecone

```bash
pip install -qU datasets==2.14.5 "pinecone[grpc]"==5.1.0
```

## Verify

```bash
pip list | grep -E "datasets|pinecone"
```