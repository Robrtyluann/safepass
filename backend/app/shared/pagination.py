from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.database import Base


def paginate[T: Base](
    session: Session, query: Select[tuple[T]], page: int, size: int
) -> tuple[list[T], int]:
    total = session.scalar(select(func.count()).select_from(query.order_by(None).subquery())) or 0
    items = list(session.scalars(query.offset((page - 1) * size).limit(size)).unique())
    return items, total
