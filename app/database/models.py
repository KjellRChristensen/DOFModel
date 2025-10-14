"""
SQLAlchemy database models for Norwegian oil fields and cable inspection
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey,
    CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class OilField(Base):
    """Main oil/gas field entity"""
    __tablename__ = 'oil_fields'

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    operator = Column(String(100), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    discovery_year = Column(Integer)
    production_start_year = Column(Integer)
    sea_area = Column(String(20), nullable=False, index=True)
    resource_type = Column(String(30), nullable=False)
    description = Column(Text)
    infrastructure_notes = Column(Text)
    estimated_resources_mmboe = Column(Float)
    hub_field_id = Column(String(50), ForeignKey('oil_fields.field_id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    location = relationship("FieldLocation", back_populates="field", uselist=False, cascade="all, delete-orphan")
    platforms = relationship("Platform", back_populates="field", cascade="all, delete-orphan")
    license_blocks = relationship("LicenseBlock", back_populates="field", cascade="all, delete-orphan")

    # Hub-satellite relationships
    satellites = relationship(
        "FieldRelationship",
        foreign_keys="FieldRelationship.hub_field_id",
        back_populates="hub_field",
        cascade="all, delete-orphan"
    )
    hub_connections = relationship(
        "FieldRelationship",
        foreign_keys="FieldRelationship.satellite_field_id",
        back_populates="satellite_field",
        cascade="all, delete-orphan"
    )

    # Cable routes
    cable_routes_from = relationship(
        "CableRoute",
        foreign_keys="CableRoute.start_field_id",
        back_populates="start_field",
        cascade="all, delete-orphan"
    )
    cable_routes_to = relationship(
        "CableRoute",
        foreign_keys="CableRoute.end_field_id",
        back_populates="end_field",
        cascade="all, delete-orphan"
    )

    cluster_memberships = relationship("ClusterMember", back_populates="field", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('producing', 'planned', 'under_development', 'shutdown', 'decommissioned')"),
        CheckConstraint("sea_area IN ('north_sea', 'norwegian_sea', 'barents_sea')"),
    )

    def __repr__(self):
        return f"<OilField(field_id='{self.field_id}', name='{self.name}', operator='{self.operator}')>"


class FieldLocation(Base):
    """Geographic location data for oil fields"""
    __tablename__ = 'field_locations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey('oil_fields.field_id'), unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    water_depth_min = Column(Float)
    water_depth_max = Column(Float)
    distance_from_shore_km = Column(Float)
    nearest_city = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    field = relationship("OilField", back_populates="location")

    __table_args__ = (
        CheckConstraint('latitude >= -90 AND latitude <= 90'),
        CheckConstraint('longitude >= -180 AND longitude <= 180'),
        Index('idx_coordinates', 'latitude', 'longitude'),
    )

    def __repr__(self):
        return f"<FieldLocation(field_id='{self.field_id}', lat={self.latitude}, lon={self.longitude})>"


class LicenseBlock(Base):
    """License blocks associated with fields"""
    __tablename__ = 'license_blocks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    block_number = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    field = relationship("OilField", back_populates="license_blocks")

    __table_args__ = (
        UniqueConstraint('field_id', 'block_number', name='uq_field_block'),
    )

    def __repr__(self):
        return f"<LicenseBlock(field_id='{self.field_id}', block='{self.block_number}')>"


class Platform(Base):
    """Individual platforms/installations within fields"""
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    platform_type = Column(String(30), nullable=False, index=True)
    installation_year = Column(Integer)
    operational = Column(Boolean, default=True, index=True)
    unmanned = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    field = relationship("OilField", back_populates="platforms")

    __table_args__ = (
        CheckConstraint("platform_type IN ('condeep', 'steel_jacket', 'fpso', 'semi_submersible', 'tlp', 'spar', 'subsea', 'unmanned', 'onshore')"),
    )

    def __repr__(self):
        return f"<Platform(name='{self.name}', type='{self.platform_type}', field='{self.field_id}')>"


class Operator(Base):
    """Operating companies"""
    __tablename__ = 'operators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(100), unique=True, nullable=False)
    country = Column(String(50))
    contact_info = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Operator(name='{self.company_name}')>"


class FieldRelationship(Base):
    """Hub-satellite and tieback relationships between fields"""
    __tablename__ = 'field_relationships'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hub_field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    satellite_field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    relationship_type = Column(String(30), default='satellite')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hub_field = relationship("OilField", foreign_keys=[hub_field_id], back_populates="satellites")
    satellite_field = relationship("OilField", foreign_keys=[satellite_field_id], back_populates="hub_connections")

    __table_args__ = (
        UniqueConstraint('hub_field_id', 'satellite_field_id', name='uq_hub_satellite'),
        CheckConstraint("relationship_type IN ('satellite', 'tieback', 'subsea_connection')"),
    )

    def __repr__(self):
        return f"<FieldRelationship(hub='{self.hub_field_id}', satellite='{self.satellite_field_id}')>"


class CableRoute(Base):
    """Submarine cables connecting installations"""
    __tablename__ = 'cable_routes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    start_field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    end_field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    cable_type = Column(String(30), nullable=False, index=True)
    length_km = Column(Float, nullable=False)
    installation_year = Column(Integer)
    operational = Column(Boolean, default=True)
    inspection_required = Column(Boolean, default=True, index=True)
    last_inspection_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    start_field = relationship("OilField", foreign_keys=[start_field_id], back_populates="cable_routes_from")
    end_field = relationship("OilField", foreign_keys=[end_field_id], back_populates="cable_routes_to")
    inspections = relationship("CableInspection", back_populates="cable_route", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("cable_type IN ('power', 'communication', 'umbilical', 'fiber_optic')"),
    )

    def __repr__(self):
        return f"<CableRoute(route_id='{self.route_id}', from='{self.start_field_id}', to='{self.end_field_id}')>"


class CableInspection(Base):
    """Inspection records for cable routes"""
    __tablename__ = 'cable_inspections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    inspection_id = Column(String(50), unique=True, nullable=False, index=True)
    cable_route_id = Column(Integer, ForeignKey('cable_routes.id'), nullable=False, index=True)
    inspection_date = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    depth = Column(Float)
    image_id = Column(String(100))  # Links to uploaded image
    condition = Column(String(20), index=True)
    detected_issues = Column(Text)  # JSON array stored as TEXT
    confidence_score = Column(Float)
    recommendations = Column(Text)  # JSON array
    inspector = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    cable_route = relationship("CableRoute", back_populates="inspections")

    __table_args__ = (
        CheckConstraint('latitude >= -90 AND latitude <= 90'),
        CheckConstraint('longitude >= -180 AND longitude <= 180'),
        CheckConstraint("condition IN ('excellent', 'good', 'fair', 'poor', 'critical', 'unknown')"),
        Index('idx_inspection_coordinates', 'latitude', 'longitude'),
    )

    def __repr__(self):
        return f"<CableInspection(id='{self.inspection_id}', route_id={self.cable_route_id}, condition='{self.condition}')>"


class InfrastructureCluster(Base):
    """Logical groupings of interconnected fields"""
    __tablename__ = 'infrastructure_clusters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hub_field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False)
    sea_area = Column(String(20), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    members = relationship("ClusterMember", back_populates="cluster", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<InfrastructureCluster(id='{self.cluster_id}', name='{self.name}')>"


class ClusterMember(Base):
    """Junction table for cluster membership"""
    __tablename__ = 'cluster_members'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(String(50), ForeignKey('infrastructure_clusters.cluster_id'), nullable=False, index=True)
    field_id = Column(String(50), ForeignKey('oil_fields.field_id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cluster = relationship("InfrastructureCluster", back_populates="members")
    field = relationship("OilField", back_populates="cluster_memberships")

    __table_args__ = (
        UniqueConstraint('cluster_id', 'field_id', name='uq_cluster_field'),
    )

    def __repr__(self):
        return f"<ClusterMember(cluster='{self.cluster_id}', field='{self.field_id}')>"
