from app.db.session import engine, Base
from app.db import models  # noqa: F401  (important: registers models)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)