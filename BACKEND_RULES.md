# Backend Development Rules

## Python Usage

**ALWAYS use `python3` explicitly, never `python`**

### Commands:
- ✅ `python3 main.py`
- ✅ `python3 test_visual_inspection.py`
- ✅ `python3 -m pip install -r requirements.txt`
- ❌ `python main.py` (NEVER use)
- ❌ `python test.py` (NEVER use)

### Why?
- Ensures Python 3.x is always used
- Avoids conflicts with Python 2.x if installed
- Consistent across all environments
- macOS compatibility

## Installation

```bash
python3 -m pip install -r requirements.txt
```

## Running the Server

```bash
python3 main.py
```

## Running Tests

```bash
python3 test_visual_inspection.py
python3 test_endpoints.sh  # If shell script
```

## Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
python3 main.py
```
