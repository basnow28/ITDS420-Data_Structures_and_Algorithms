# src — package overview

This is the top-level Python package for the friend-recommendation system. It contains two sub-packages that cleanly separate infrastructure from the domain model.

## Sub-packages

| Package | Purpose |
|---------|---------|
| `data_structures/` | Low-level building blocks: a custom hash map and the linked-list node it is built on |
| `models/` | Domain entities: the `User` class |

## How they interact

`CustomHashMap` (in `data_structures/`) imports `User` (from `models/`) as the value type it stores. Keys are username strings; values are `User` objects. The `User` class itself has no dependency on `data_structures/`, keeping the domain layer free of infrastructure concerns.

```
models/User  ←  data_structures/CustomHashMap
                        ↑
                data_structures/Node
```

## Public API

Both sub-packages re-export their classes from their `__init__.py`, so callers can import directly from the sub-package:

```python
from src.data_structures import Node, CustomHashMap
from src.models import User
```
