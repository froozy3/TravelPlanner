from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class BaseDB(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)

    @declared_attr
    def __tablename__(cls) -> str:
        if cls.__name__.endswith("DB"):
            return cls.__name__[:-2].lower() + "s"
        return cls.__name__.lower() + "s"
