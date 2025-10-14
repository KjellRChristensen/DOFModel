# SQLite Database Design for Norwegian Oil Fields

## Overview

This document outlines the database design for storing Norwegian oil and gas field data, optimized for underwater cable inspection and MapKit integration.

---

## Database Entities

### 1. **OilFields** (Main Entity)
Central table storing core oil/gas field information.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `field_id` (TEXT, UNIQUE, NOT NULL) - e.g., "EKOFISK", "STATFJORD"
- `name` (TEXT, NOT NULL) - Field display name
- `operator` (TEXT, NOT NULL) - Operating company
- `status` (TEXT, NOT NULL) - "producing", "planned", "shutdown", etc.
- `discovery_year` (INTEGER)
- `production_start_year` (INTEGER)
- `sea_area` (TEXT, NOT NULL) - "north_sea", "norwegian_sea", "barents_sea"
- `resource_type` (TEXT, NOT NULL) - "oil", "gas", "oil_and_gas", "condensate"
- `description` (TEXT)
- `infrastructure_notes` (TEXT)
- `estimated_resources_mmboe` (REAL) - Million barrels of oil equivalent
- `hub_field_id` (TEXT) - Foreign key to parent hub field if satellite
- `created_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP)
- `updated_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP)

**Indexes:**
- `idx_field_id` on `field_id`
- `idx_operator` on `operator`
- `idx_status` on `status`
- `idx_sea_area` on `sea_area`

**Rationale:**
- Central table for field metadata
- `field_id` as unique business key for external references
- Denormalized `sea_area` for fast filtering
- `hub_field_id` enables satellite field relationships

---

### 2. **FieldLocations**
Geographic coordinates and location data (1-to-1 with OilFields).

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `field_id` (TEXT, UNIQUE, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `latitude` (REAL, NOT NULL)
- `longitude` (REAL, NOT NULL)
- `water_depth_min` (REAL) - in meters
- `water_depth_max` (REAL) - in meters
- `distance_from_shore_km` (REAL)
- `nearest_city` (TEXT)
- `created_at` (DATETIME)

**Indexes:**
- `idx_field_location` on `field_id`
- `idx_coordinates` on `latitude, longitude` (for spatial queries)

**Rationale:**
- Separate table for geographic data to optimize spatial queries
- Enables efficient radius searches for MapKit
- Keeps location data isolated for potential future GIS extensions

---

### 3. **LicenseBlocks**
License blocks associated with fields (many-to-many relationship).

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `block_number` (TEXT, NOT NULL) - e.g., "2/4", "33/9"
- `created_at` (DATETIME)

**Indexes:**
- `idx_field_blocks` on `field_id`
- `idx_block_number` on `block_number`

**Unique Constraint:** (`field_id`, `block_number`)

**Rationale:**
- Fields can span multiple license blocks
- Enables queries like "show all fields in block 34/10"
- Junction table pattern for many-to-many

---

### 4. **Platforms**
Individual platforms/installations within fields.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `name` (TEXT, NOT NULL) - e.g., "Statfjord A", "Troll A"
- `platform_type` (TEXT, NOT NULL) - "condeep", "fpso", "tlp", "steel_jacket", etc.
- `installation_year` (INTEGER)
- `operational` (BOOLEAN, DEFAULT TRUE)
- `unmanned` (BOOLEAN, DEFAULT FALSE)
- `description` (TEXT)
- `created_at` (DATETIME)

**Indexes:**
- `idx_field_platforms` on `field_id`
- `idx_platform_type` on `platform_type`
- `idx_operational` on `operational`

**Rationale:**
- One field can have multiple platforms (e.g., Statfjord A, B, C)
- Platform-level tracking for maintenance and cable routing
- Type classification for infrastructure analysis

---

### 5. **Operators**
Company information (normalized reference table).

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `company_name` (TEXT, UNIQUE, NOT NULL)
- `country` (TEXT)
- `contact_info` (TEXT)
- `created_at` (DATETIME)

**Rationale:**
- Normalize operator data to avoid duplication
- Enables operator-level analytics
- Future: contact information for inspection coordination

---

### 6. **FieldRelationships**
Tracks hub-satellite and tieback relationships.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `hub_field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `satellite_field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `relationship_type` (TEXT) - "satellite", "tieback", "subsea_connection"
- `created_at` (DATETIME)

**Indexes:**
- `idx_hub_field` on `hub_field_id`
- `idx_satellite_field` on `satellite_field_id`

**Unique Constraint:** (`hub_field_id`, `satellite_field_id`)

**Rationale:**
- Explicit many-to-many relationships between fields
- Essential for cable routing (satellites connect to hubs)
- Enables network topology queries

---

### 7. **CableRoutes**
Submarine cables connecting installations.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `route_id` (TEXT, UNIQUE, NOT NULL)
- `name` (TEXT, NOT NULL)
- `start_field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `end_field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `cable_type` (TEXT, NOT NULL) - "power", "communication", "umbilical"
- `length_km` (REAL, NOT NULL)
- `installation_year` (INTEGER)
- `operational` (BOOLEAN, DEFAULT TRUE)
- `inspection_required` (BOOLEAN, DEFAULT TRUE)
- `last_inspection_date` (DATETIME)
- `notes` (TEXT)
- `created_at` (DATETIME)

**Indexes:**
- `idx_start_field` on `start_field_id`
- `idx_end_field` on `end_field_id`
- `idx_cable_type` on `cable_type`
- `idx_inspection_required` on `inspection_required`

**Rationale:**
- **Core table for cable inspection workflow**
- Links fields for infrastructure mapping
- Tracks inspection status and requirements
- Enables queries like "show all cables needing inspection"

---

### 8. **CableInspections**
Inspection history for cable routes.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `inspection_id` (TEXT, UNIQUE, NOT NULL)
- `cable_route_id` (INTEGER, NOT NULL, FOREIGN KEY → CableRoutes.id)
- `inspection_date` (DATETIME, NOT NULL)
- `latitude` (REAL)
- `longitude` (REAL)
- `depth` (REAL)
- `image_id` (TEXT) - Links to uploaded image
- `condition` (TEXT) - "excellent", "good", "fair", "poor", "critical"
- `detected_issues` (TEXT) - JSON array stored as TEXT
- `confidence_score` (REAL)
- `recommendations` (TEXT) - JSON array
- `inspector` (TEXT)
- `notes` (TEXT)
- `created_at` (DATETIME)

**Indexes:**
- `idx_cable_route` on `cable_route_id`
- `idx_inspection_date` on `inspection_date`
- `idx_condition` on `condition`
- `idx_coordinates` on `latitude, longitude`

**Rationale:**
- **Integrates with image analysis API**
- Historical record of all inspections
- Geo-tagged for MapKit visualization
- Links to CableRoutes for complete audit trail

---

### 9. **InfrastructureClusters**
Logical groupings of interconnected fields.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `cluster_id` (TEXT, UNIQUE, NOT NULL)
- `name` (TEXT, NOT NULL) - e.g., "Greater Ekofisk Area"
- `hub_field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `sea_area` (TEXT, NOT NULL)
- `description` (TEXT)
- `created_at` (DATETIME)

**Rationale:**
- Groups related fields (e.g., Ekofisk + Eldfisk + Embla + Tor)
- Useful for regional analysis and planning
- Simplifies cable network visualization

---

### 10. **ClusterMembers**
Junction table for cluster membership.

**Columns:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `cluster_id` (TEXT, NOT NULL, FOREIGN KEY → InfrastructureClusters.cluster_id)
- `field_id` (TEXT, NOT NULL, FOREIGN KEY → OilFields.field_id)
- `created_at` (DATETIME)

**Unique Constraint:** (`cluster_id`, `field_id`)

**Rationale:**
- Many-to-many: fields can belong to multiple clusters
- Flexible grouping for analysis

---

## Entity Relationship Diagram (Textual)

```
OilFields (1) ──────────── (1) FieldLocations
    │
    │ (1)
    │
    └──────────────────────── (N) Platforms
    │
    │ (1)
    │
    ├──────────────────────── (N) LicenseBlocks
    │
    │ (1)
    │
    ├──────────────────────── (N) FieldRelationships (as hub)
    │
    │ (1)
    │
    ├──────────────────────── (N) FieldRelationships (as satellite)
    │
    │ (1)
    │
    ├──────────────────────── (N) CableRoutes (as start)
    │
    │ (1)
    │
    ├──────────────────────── (N) CableRoutes (as end)
    │
    │ (1)
    │
    └──────────────────────── (N) ClusterMembers

CableRoutes (1) ──────────── (N) CableInspections

InfrastructureClusters (1) ── (N) ClusterMembers
```

---

## Design Rationale & Benefits

### 1. **Normalization vs. Denormalization**
- **Normalized:** Operators, LicenseBlocks, Platforms (reduce duplication)
- **Denormalized:** `sea_area`, `status` in OilFields (optimize queries)
- **Balance:** Fast reads for common queries, minimal write overhead

### 2. **Spatial Query Optimization**
- Separate `FieldLocations` table with composite index on `(latitude, longitude)`
- Enables efficient radius searches: "Find all fields within 50km of 60.5°N, 2.8°E"
- Critical for MapKit "nearby inspections" feature

### 3. **Cable Inspection Workflow**
- `CableRoutes` → `CableInspections` relationship
- Direct integration with `/api/v1/analyze` endpoint
- Each inspection links to cable route + GPS coordinates + image
- Historical tracking for compliance and maintenance scheduling

### 4. **Hierarchical Relationships**
- Hub fields (e.g., Ekofisk) link to satellites (e.g., Eldfisk, Embla)
- `FieldRelationships` table enables network graph queries
- Essential for understanding cable interconnections

### 5. **Extensibility**
- JSON fields in `CableInspections` for flexible issue tracking
- `infrastructure_notes` TEXT fields for unstructured data
- Easy to add new tables (e.g., ProductionData, MaintenanceSchedule)

### 6. **Integration with Existing API**
- `CableInspections.image_id` links to uploaded images
- `condition` maps to `CableCondition` enum in API
- `detected_issues` stores ML analysis results
- Seamless flow: Upload image → Analyze → Store results → Display on map

### 7. **Performance Considerations**
- Indexes on foreign keys for JOIN performance
- Composite indexes for common query patterns
- SQLite is lightweight, perfect for this dataset size (~100 fields)
- Can migrate to PostgreSQL later if needed

---

## Key Queries Enabled

### 1. Find all fields operated by Equinor in North Sea
```sql
SELECT * FROM OilFields
WHERE operator = 'Equinor Energy AS'
AND sea_area = 'north_sea';
```

### 2. Find fields within 50km of a coordinate
```sql
SELECT f.*, l.latitude, l.longitude
FROM OilFields f
JOIN FieldLocations l ON f.field_id = l.field_id
WHERE (
  (l.latitude - 60.5) * (l.latitude - 60.5) +
  (l.longitude - 2.8) * (l.longitude - 2.8)
) < 0.45;  -- Rough approximation for 50km
```

### 3. Find all satellites connected to Ekofisk
```sql
SELECT sf.*
FROM FieldRelationships fr
JOIN OilFields sf ON fr.satellite_field_id = sf.field_id
WHERE fr.hub_field_id = 'EKOFISK';
```

### 4. Find cables needing inspection
```sql
SELECT cr.*,
  f_start.name as start_field,
  f_end.name as end_field
FROM CableRoutes cr
LEFT JOIN CableInspections ci ON cr.id = ci.cable_route_id
JOIN OilFields f_start ON cr.start_field_id = f_start.field_id
JOIN OilFields f_end ON cr.end_field_id = f_end.field_id
WHERE cr.inspection_required = TRUE
AND (ci.inspection_date IS NULL OR ci.inspection_date < date('now', '-6 months'));
```

### 5. Get inspection history for a cable
```sql
SELECT * FROM CableInspections
WHERE cable_route_id = (
  SELECT id FROM CableRoutes WHERE route_id = 'ROUTE_001'
)
ORDER BY inspection_date DESC;
```

---

## Data Integrity Constraints

1. **Foreign Keys:** Enforce referential integrity
2. **Unique Constraints:** Prevent duplicate fields, blocks, relationships
3. **NOT NULL:** Required fields cannot be empty
4. **CHECK Constraints:**
   - `latitude BETWEEN -90 AND 90`
   - `longitude BETWEEN -180 AND 180`
   - `status IN ('producing', 'planned', 'shutdown', ...)`

---

## Migration Path

1. **Phase 1:** Create schema with core tables (OilFields, FieldLocations, Platforms)
2. **Phase 2:** Load data from norwegian_oil_fields.md
3. **Phase 3:** Add CableRoutes and CableInspections (integrate with API)
4. **Phase 4:** Populate relationships and clusters
5. **Phase 5:** Add production/maintenance tracking tables (future)

---

## Next Steps

Once you approve this design, I will:
1. Create SQLAlchemy models matching this schema
2. Write database initialization script
3. Create data migration script from MD → SQLite
4. Update FastAPI endpoints to use database instead of in-memory storage
5. Add query utilities for common operations

**Questions for you:**
- Do you want to track production volumes (daily/monthly)?
- Should we add maintenance schedules and work orders?
- Do you need user/authentication tables for inspector tracking?
- Should cable routes store waypoints (not just start/end)?
