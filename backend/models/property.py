from sqlalchemy import Column, Integer, String, Numeric, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    property_type = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    price = Column(Integer, nullable=True)
    beds = Column(Integer, nullable=True)
    baths = Column(Numeric(4, 1), nullable=True)
    neighborhood = Column(String, nullable=True)
    sqft = Column(Integer, nullable=True)
    lot_size = Column(Integer, nullable=True)
    year_built = Column(Integer, nullable=True)
    days_on_market = Column(Integer, nullable=True)
    hoa_month = Column(Numeric(10, 2), nullable=True)
    listing_status = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    url = Column(String, nullable=True)
