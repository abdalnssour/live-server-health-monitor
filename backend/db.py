"""
Database configuration using SQLAlchemy Core
"""
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func

# Database URL
DATABASE_URL = "postgresql://health_user:Enssour@localhost/health_monitor"

# Create engine with echo=False to reduce noise
engine = create_engine(DATABASE_URL, echo=False)

# Create metadata
metadata = MetaData()

# Define readings table
readings = Table(
    'readings',
    metadata,
    Column('id', Integer, primary_key=True),  # Primary key is auto-indexed
    Column('value', Float, nullable=False),
    Column('status', String(20), nullable=False, server_default='ok'),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

def get_engine():
    """Get database engine"""
    return engine

def get_metadata():
    """Get metadata"""
    return metadata

def get_readings_table():
    """Get readings table"""
    return readings