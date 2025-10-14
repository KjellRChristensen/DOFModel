"""
Database query utilities for common operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import math

from .models import (
    OilField, FieldLocation, Platform, LicenseBlock,
    FieldRelationship, CableRoute, CableInspection,
    InfrastructureCluster, ClusterMember
)


# ===== Oil Field Queries =====

def get_all_fields(db: Session, skip: int = 0, limit: int = 100) -> List[OilField]:
    """Get all oil fields with pagination"""
    return db.query(OilField).offset(skip).limit(limit).all()


def get_field_by_id(db: Session, field_id: str) -> Optional[OilField]:
    """Get oil field by field_id"""
    return db.query(OilField).filter(OilField.field_id == field_id).first()


def get_fields_by_operator(db: Session, operator: str) -> List[OilField]:
    """Get all fields operated by a specific company"""
    return db.query(OilField).filter(OilField.operator == operator).all()


def get_fields_by_sea_area(db: Session, sea_area: str) -> List[OilField]:
    """Get all fields in a specific sea area"""
    return db.query(OilField).filter(OilField.sea_area == sea_area).all()


def get_fields_by_status(db: Session, status: str) -> List[OilField]:
    """Get all fields with a specific status"""
    return db.query(OilField).filter(OilField.status == status).all()


def get_producing_fields(db: Session) -> List[OilField]:
    """Get all currently producing fields"""
    return get_fields_by_status(db, "producing")


def search_fields(db: Session, query: str) -> List[OilField]:
    """Search fields by name or field_id"""
    search = f"%{query}%"
    return db.query(OilField).filter(
        or_(
            OilField.name.ilike(search),
            OilField.field_id.ilike(search),
            OilField.description.ilike(search)
        )
    ).all()


# ===== Location-based Queries =====

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers using Haversine formula
    """
    R = 6371  # Earth radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_fields_near_location(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 50.0
) -> List[Tuple[OilField, float]]:
    """
    Get all fields within radius_km of a coordinate
    Returns list of (field, distance_km) tuples sorted by distance
    """
    fields_with_distance = []

    # Get all fields with locations
    fields = db.query(OilField).join(FieldLocation).all()

    for field in fields:
        if field.location:
            distance = haversine_distance(
                latitude, longitude,
                field.location.latitude, field.location.longitude
            )
            if distance <= radius_km:
                fields_with_distance.append((field, distance))

    # Sort by distance
    fields_with_distance.sort(key=lambda x: x[1])
    return fields_with_distance


def get_nearest_fields(
    db: Session,
    latitude: float,
    longitude: float,
    count: int = 5
) -> List[Tuple[OilField, float]]:
    """
    Get the N nearest fields to a coordinate
    Returns list of (field, distance_km) tuples
    """
    all_fields = db.query(OilField).join(FieldLocation).all()

    fields_with_distance = []
    for field in all_fields:
        if field.location:
            distance = haversine_distance(
                latitude, longitude,
                field.location.latitude, field.location.longitude
            )
            fields_with_distance.append((field, distance))

    # Sort and return top N
    fields_with_distance.sort(key=lambda x: x[1])
    return fields_with_distance[:count]


# ===== Platform Queries =====

def get_platforms_by_field(db: Session, field_id: str) -> List[Platform]:
    """Get all platforms for a specific field"""
    return db.query(Platform).filter(Platform.field_id == field_id).all()


def get_platforms_by_type(db: Session, platform_type: str) -> List[Platform]:
    """Get all platforms of a specific type"""
    return db.query(Platform).filter(Platform.platform_type == platform_type).all()


def get_operational_platforms(db: Session) -> List[Platform]:
    """Get all operational platforms"""
    return db.query(Platform).filter(Platform.operational == True).all()


# ===== Field Relationship Queries =====

def get_satellite_fields(db: Session, hub_field_id: str) -> List[OilField]:
    """Get all satellite fields connected to a hub field"""
    relationships = db.query(FieldRelationship).filter(
        FieldRelationship.hub_field_id == hub_field_id
    ).all()

    satellite_ids = [r.satellite_field_id for r in relationships]
    return db.query(OilField).filter(OilField.field_id.in_(satellite_ids)).all()


def get_hub_field(db: Session, satellite_field_id: str) -> Optional[OilField]:
    """Get the hub field for a satellite field"""
    relationship = db.query(FieldRelationship).filter(
        FieldRelationship.satellite_field_id == satellite_field_id
    ).first()

    if relationship:
        return db.query(OilField).filter(
            OilField.field_id == relationship.hub_field_id
        ).first()
    return None


def get_field_network(db: Session, field_id: str) -> dict:
    """
    Get complete network of connected fields (hub and all satellites)
    Returns dict with hub field and list of satellite fields
    """
    field = get_field_by_id(db, field_id)
    if not field:
        return None

    # Check if this field is a hub
    satellites = get_satellite_fields(db, field_id)

    # Check if this field is a satellite
    hub = get_hub_field(db, field_id)

    return {
        "field": field,
        "hub": hub,
        "satellites": satellites,
        "is_hub": len(satellites) > 0,
        "is_satellite": hub is not None
    }


# ===== Cable Route Queries =====

def get_cable_routes_for_field(db: Session, field_id: str) -> List[CableRoute]:
    """Get all cable routes connected to a field (incoming or outgoing)"""
    return db.query(CableRoute).filter(
        or_(
            CableRoute.start_field_id == field_id,
            CableRoute.end_field_id == field_id
        )
    ).all()


def get_cables_needing_inspection(
    db: Session,
    days_since_last_inspection: int = 180
) -> List[CableRoute]:
    """
    Get cables that need inspection
    (no inspection or last inspection older than specified days)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_since_last_inspection)

    return db.query(CableRoute).filter(
        and_(
            CableRoute.inspection_required == True,
            or_(
                CableRoute.last_inspection_date == None,
                CableRoute.last_inspection_date < cutoff_date
            )
        )
    ).all()


def get_cable_route_by_id(db: Session, route_id: str) -> Optional[CableRoute]:
    """Get cable route by route_id"""
    return db.query(CableRoute).filter(CableRoute.route_id == route_id).first()


# ===== Cable Inspection Queries =====

def get_inspections_for_cable(
    db: Session,
    cable_route_id: int,
    limit: int = 50
) -> List[CableInspection]:
    """Get inspection history for a cable route"""
    return db.query(CableInspection).filter(
        CableInspection.cable_route_id == cable_route_id
    ).order_by(CableInspection.inspection_date.desc()).limit(limit).all()


def get_latest_inspection(
    db: Session,
    cable_route_id: int
) -> Optional[CableInspection]:
    """Get most recent inspection for a cable route"""
    return db.query(CableInspection).filter(
        CableInspection.cable_route_id == cable_route_id
    ).order_by(CableInspection.inspection_date.desc()).first()


def get_inspections_by_condition(
    db: Session,
    condition: str
) -> List[CableInspection]:
    """Get all inspections with a specific condition rating"""
    return db.query(CableInspection).filter(
        CableInspection.condition == condition
    ).all()


def get_recent_inspections(
    db: Session,
    days: int = 30,
    limit: int = 100
) -> List[CableInspection]:
    """Get recent inspections within the last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    return db.query(CableInspection).filter(
        CableInspection.inspection_date >= cutoff_date
    ).order_by(CableInspection.inspection_date.desc()).limit(limit).all()


def get_inspections_near_location(
    db: Session,
    latitude: float,
    longitude: float,
    radius_km: float = 10.0
) -> List[Tuple[CableInspection, float]]:
    """
    Get inspections near a location
    Returns list of (inspection, distance_km) tuples
    """
    inspections_with_distance = []

    # Get all inspections with coordinates
    inspections = db.query(CableInspection).filter(
        and_(
            CableInspection.latitude != None,
            CableInspection.longitude != None
        )
    ).all()

    for inspection in inspections:
        distance = haversine_distance(
            latitude, longitude,
            inspection.latitude, inspection.longitude
        )
        if distance <= radius_km:
            inspections_with_distance.append((inspection, distance))

    # Sort by distance
    inspections_with_distance.sort(key=lambda x: x[1])
    return inspections_with_distance


# ===== Cluster Queries =====

def get_cluster_by_id(db: Session, cluster_id: str) -> Optional[InfrastructureCluster]:
    """Get infrastructure cluster by cluster_id"""
    return db.query(InfrastructureCluster).filter(
        InfrastructureCluster.cluster_id == cluster_id
    ).first()


def get_fields_in_cluster(db: Session, cluster_id: str) -> List[OilField]:
    """Get all fields in a cluster"""
    members = db.query(ClusterMember).filter(
        ClusterMember.cluster_id == cluster_id
    ).all()

    field_ids = [m.field_id for m in members]
    return db.query(OilField).filter(OilField.field_id.in_(field_ids)).all()


def get_clusters_for_field(db: Session, field_id: str) -> List[InfrastructureCluster]:
    """Get all clusters a field belongs to"""
    members = db.query(ClusterMember).filter(
        ClusterMember.field_id == field_id
    ).all()

    cluster_ids = [m.cluster_id for m in members]
    return db.query(InfrastructureCluster).filter(
        InfrastructureCluster.cluster_id.in_(cluster_ids)
    ).all()


# ===== Statistics Queries =====

def get_field_statistics(db: Session) -> dict:
    """Get overall statistics about oil fields"""
    total_fields = db.query(OilField).count()
    producing_fields = db.query(OilField).filter(OilField.status == "producing").count()

    by_sea_area = db.query(
        OilField.sea_area,
        func.count(OilField.id)
    ).group_by(OilField.sea_area).all()

    by_operator = db.query(
        OilField.operator,
        func.count(OilField.id)
    ).group_by(OilField.operator).order_by(func.count(OilField.id).desc()).all()

    return {
        "total_fields": total_fields,
        "producing_fields": producing_fields,
        "by_sea_area": {area: count for area, count in by_sea_area},
        "by_operator": {operator: count for operator, count in by_operator[:10]},
        "total_platforms": db.query(Platform).count(),
        "operational_platforms": db.query(Platform).filter(Platform.operational == True).count()
    }


def get_cable_statistics(db: Session) -> dict:
    """Get statistics about cable routes and inspections"""
    total_cables = db.query(CableRoute).count()
    operational_cables = db.query(CableRoute).filter(CableRoute.operational == True).count()
    cables_need_inspection = len(get_cables_needing_inspection(db, days_since_last_inspection=180))

    total_inspections = db.query(CableInspection).count()

    by_condition = db.query(
        CableInspection.condition,
        func.count(CableInspection.id)
    ).group_by(CableInspection.condition).all()

    return {
        "total_cables": total_cables,
        "operational_cables": operational_cables,
        "cables_needing_inspection": cables_need_inspection,
        "total_inspections": total_inspections,
        "inspections_by_condition": {condition: count for condition, count in by_condition}
    }
