# Database Usage Guide

## Quick Start

### 1. Initialize and Migrate Data

```bash
# Install dependencies
pip install -r requirements.txt

# Run migration script
python scripts/migrate_data.py
```

This will:
- Create SQLite database at `data/oil_fields.db`
- Create all tables
- Load ~20 sample oil fields
- Set up relationships and clusters

### 2. Using the Database in Python

```python
from app.database.database import get_db_session
from app.database.models import OilField
from app.database import queries

# Simple query
with get_db_session() as db:
    field = queries.get_field_by_id(db, "EKOFISK")
    print(f"{field.name} - {field.operator}")
```

---

## Common Query Examples

### Find Fields Near a Location

```python
from app.database.database import get_db_session
from app.database import queries

with get_db_session() as db:
    # Find fields within 50km of Bergen area
    nearby_fields = queries.get_fields_near_location(
        db,
        latitude=60.5,
        longitude=2.8,
        radius_km=50
    )

    for field, distance in nearby_fields:
        print(f"{field.name}: {distance:.1f} km away")
```

### Get All Satellites of a Hub Field

```python
with get_db_session() as db:
    satellites = queries.get_satellite_fields(db, "EKOFISK")

    for sat in satellites:
        print(f"- {sat.name} ({sat.field_id})")
```

### Find Cables Needing Inspection

```python
with get_db_session() as db:
    # Get cables not inspected in last 6 months
    cables = queries.get_cables_needing_inspection(db, days_since_last_inspection=180)

    for cable in cables:
        print(f"{cable.name}: {cable.start_field_id} → {cable.end_field_id}")
        if cable.last_inspection_date:
            print(f"  Last inspected: {cable.last_inspection_date}")
        else:
            print(f"  Never inspected")
```

### Search Fields by Name/ID

```python
with get_db_session() as db:
    results = queries.search_fields(db, "stat")  # Finds Statfjord fields

    for field in results:
        print(f"{field.field_id}: {field.name}")
```

### Get Field Network (Hub + Satellites)

```python
with get_db_session() as db:
    network = queries.get_field_network(db, "GULLFAKS")

    print(f"Field: {network['field'].name}")
    print(f"Is Hub: {network['is_hub']}")
    print(f"Is Satellite: {network['is_satellite']}")

    if network['satellites']:
        print("Satellites:")
        for sat in network['satellites']:
            print(f"  - {sat.name}")
```

### Get Statistics

```python
with get_db_session() as db:
    stats = queries.get_field_statistics(db)

    print(f"Total Fields: {stats['total_fields']}")
    print(f"Producing: {stats['producing_fields']}")
    print("\nBy Sea Area:")
    for area, count in stats['by_sea_area'].items():
        print(f"  {area}: {count}")
```

---

## Using with FastAPI

### Add Database Dependency to Endpoints

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database import queries

@app.get("/api/v1/fields")
def get_fields(
    sea_area: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if sea_area:
        fields = queries.get_fields_by_sea_area(db, sea_area)
    else:
        fields = queries.get_all_fields(db)

    return fields


@app.get("/api/v1/fields/{field_id}")
def get_field(field_id: str, db: Session = Depends(get_db)):
    field = queries.get_field_by_id(db, field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field


@app.get("/api/v1/fields/nearby")
def get_nearby_fields(
    latitude: float,
    longitude: float,
    radius_km: float = 50,
    db: Session = Depends(get_db)
):
    fields_with_distance = queries.get_fields_near_location(
        db, latitude, longitude, radius_km
    )

    return [
        {
            "field": field,
            "distance_km": round(distance, 2)
        }
        for field, distance in fields_with_distance
    ]
```

---

## Adding Cable Inspection Data

### When Image is Analyzed

```python
from app.database.database import get_db_session
from app.database.models import CableInspection
from datetime import datetime
import uuid
import json

def save_inspection_result(
    cable_route_id: int,
    latitude: float,
    longitude: float,
    depth: float,
    image_id: str,
    analysis_result: dict
):
    with get_db_session() as db:
        inspection = CableInspection(
            inspection_id=str(uuid.uuid4()),
            cable_route_id=cable_route_id,
            inspection_date=datetime.utcnow(),
            latitude=latitude,
            longitude=longitude,
            depth=depth,
            image_id=image_id,
            condition=analysis_result.get("cable_condition", "unknown"),
            detected_issues=json.dumps(analysis_result.get("detected_issues", [])),
            confidence_score=analysis_result.get("confidence_score", 0.0),
            recommendations=json.dumps(analysis_result.get("recommendations", []))
        )
        db.add(inspection)
        db.commit()

        # Update cable's last inspection date
        cable = db.query(CableRoute).filter_by(id=cable_route_id).first()
        if cable:
            cable.last_inspection_date = datetime.utcnow()
            db.commit()

        return inspection
```

---

## Raw SQL Queries (Advanced)

```python
from sqlalchemy import text

with get_db_session() as db:
    # Complex query not covered by helper functions
    result = db.execute(
        text("""
        SELECT f.name, f.operator, COUNT(p.id) as platform_count
        FROM oil_fields f
        LEFT JOIN platforms p ON f.field_id = p.field_id
        WHERE f.sea_area = :sea_area
        GROUP BY f.field_id
        ORDER BY platform_count DESC
        """),
        {"sea_area": "north_sea"}
    )

    for row in result:
        print(f"{row.name}: {row.platform_count} platforms")
```

---

## Database Management

### Reset Database (Development Only)

```python
from app.database.database import reset_db

# WARNING: This drops all tables and data!
reset_db()
```

### Add New Cable Route

```python
from app.database.database import get_db_session
from app.database.models import CableRoute

with get_db_session() as db:
    cable = CableRoute(
        route_id="ROUTE_EKOFISK_STATFJORD",
        name="Ekofisk to Statfjord Power Cable",
        start_field_id="EKOFISK",
        end_field_id="STATFJORD",
        cable_type="power",
        length_km=450.0,
        installation_year=2005,
        operational=True,
        inspection_required=True
    )
    db.add(cable)
    db.commit()
```

---

## Performance Tips

1. **Use Indexes**: Queries on `field_id`, `latitude/longitude`, `status` are optimized with indexes

2. **Batch Operations**: When adding multiple records, add them all before `commit()`

```python
with get_db_session() as db:
    for data in bulk_data:
        field = OilField(**data)
        db.add(field)
    db.commit()  # Single commit for all
```

3. **Eager Loading**: Use `.options()` for relationships

```python
from sqlalchemy.orm import joinedload

fields = db.query(OilField).options(
    joinedload(OilField.location),
    joinedload(OilField.platforms)
).all()
```

4. **Limit Results**: Always use pagination for large result sets

```python
fields = queries.get_all_fields(db, skip=0, limit=50)
```

---

## Database Location

- **Development**: `data/oil_fields.db`
- **Production**: Configure via `DATABASE_URL` environment variable

## Backup

```bash
# SQLite backup
cp data/oil_fields.db data/oil_fields_backup_$(date +%Y%m%d).db
```

---

## Next Steps

1. Add more fields to `scripts/migrate_data.py`
2. Create cable routes between fields
3. Integrate inspection data from API
4. Build MapKit visualization with location queries
