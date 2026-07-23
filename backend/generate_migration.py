"""Generate Alembic migration from model metadata"""
import sys
import os
sys.path.insert(0, "C:/Users/fahim/child-dna/backend")

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, MetaData, text
from app.database.base import Base
from app.models.guardian import Guardian
from app.models.child import Child
from app.models.child_token import ChildToken
from app.models.rescue_session import RescueSession
from app.models.timeline_event import TimelineEvent
from app.models.reunion_record import ReunionRecord

# Create a temporary SQLite database for migration generation
engine = create_engine("sqlite:///:memory:")

# Get the metadata
target_metadata = Base.metadata

# Create the migration
config = Config("alembic.ini")
script = ScriptDirectory.from_config(config)

# Create the revision
with engine.connect() as conn:
    context = MigrationContext.configure(conn)
    ops = Operations(context)
    
    # Create tables
    for table in target_metadata.tables.values():
        table.create(conn)
    
    # Generate the migration
    script.generate_revision(
        "initial",
        "Initial migration - Core domain models",
        head="base",
        splice=False,
    )

print("Migration generated successfully!")