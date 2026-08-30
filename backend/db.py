from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func

# Database URL
DATABASE_URL = "postgresql://health_user:Enssour@localhost/health_monitor"

# Create engine
engine = create_engine(DATABASE_URL)

# Create metadata
metadata = MetaData()

# Define readings table
readings = Table(
    'readings',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('value', Float, nullable=False),
    Column('status', String(20), nullable=False, server_default='ok'),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)

def get_engine():
    return engine

def get_metadata():
    return metadata

def get_readings_table():
    return readings