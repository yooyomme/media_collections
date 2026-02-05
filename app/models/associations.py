from sqlalchemy import Table, Column, ForeignKey, Integer, UUID
from app.models.base import Base

# many-to-many relations
# table1_table2_association = Table(
#     "table1_table2",
#     Base.metadata,
#     Column("table1_id", ForeignKey("table1.id"), index=True, primary_key=True),
#     Column("table2_id", ForeignKey("table2.id"), index=True, primary_key=True),
# )