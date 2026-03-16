from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.property import Property
from backend.config import settings


async def search_properties(
    db: AsyncSession,
    min_price: int | None = None,
    max_price: int | None = None,
    min_beds: int | None = None,
    max_beds: int | None = None,
    min_baths: float | None = None,
    location: str | None = None,
    property_type: str | None = None,
    min_sqft: int | None = None,
    max_sqft: int | None = None,
    min_year_built: int | None = None,
    listing_status: str | None = None,
    max_results: int | None = None,
) -> dict:
    filters = []

    if min_price is not None:
        filters.append(Property.price >= min_price)
    if max_price is not None:
        filters.append(Property.price <= max_price)
    if min_beds is not None:
        filters.append(Property.beds >= min_beds)
    if max_beds is not None:
        filters.append(Property.beds <= max_beds)
    if min_baths is not None:
        filters.append(Property.baths >= min_baths)
    if min_sqft is not None:
        filters.append(Property.sqft >= min_sqft)
    if max_sqft is not None:
        filters.append(Property.sqft <= max_sqft)
    if min_year_built is not None:
        filters.append(Property.year_built >= min_year_built)
    if location is not None:
        filters.append(
            or_(
                Property.city.ilike(f"%{location}%"),
                Property.neighborhood.ilike(f"%{location}%"),
            )
        )
    if property_type is not None:
        filters.append(Property.property_type.ilike(f"%{property_type}%"))
    if listing_status is not None:
        filters.append(Property.listing_status.ilike(f"%{listing_status}%"))

    limit = max_results if max_results is not None else settings.max_results

    count_q = select(func.count()).select_from(Property)
    if filters:
        count_q = count_q.where(*filters)
    total_found = (await db.execute(count_q)).scalar_one()

    main_q = select(Property)
    if filters:
        main_q = main_q.where(*filters)
    main_q = main_q.order_by(Property.price.asc()).limit(limit)
    rows = (await db.execute(main_q)).unique().scalars().all()

    applied = {
        k: v for k, v in {
            "min_price": min_price,
            "max_price": max_price,
            "min_beds": min_beds,
            "max_beds": max_beds,
            "min_baths": min_baths,
            "location": location,
            "property_type": property_type,
            "min_sqft": min_sqft,
            "max_sqft": max_sqft,
            "min_year_built": min_year_built,
            "listing_status": listing_status,
            "max_results": limit,
        }.items()
        if v is not None
    }

    return {
        "total_found": total_found,
        "properties": [
            {
                "price": p.price,
                "beds": p.beds,
                "baths": float(p.baths) if p.baths is not None else None,
                "sqft": p.sqft,
                "address": p.address,
                "city": p.city,
                "neighborhood": p.neighborhood,
                "property_type": p.property_type,
                "year_built": p.year_built,
                "listing_status": p.listing_status,
                "url": p.url,
            }
            for p in rows
        ],
        "search_criteria": applied,
    }
