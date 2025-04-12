from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class Base(DeclarativeBase):
    pass


class School(Base):
    __tablename__ = 'schools'
    SCHL_CODE: Mapped[str] = mapped_column(primary_key=True, index=True)
    SCHL_NAME = Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<School SCHL_CODE={self.SCHL_CODE}, SCHL_NAME={self.SCHL_NAME})>"
    
class Department(Base):
    __tablename__ = 'departments'
    SCHL_CODE: Mapped[str] = mapped_column(ForeignKey('school.SCHL_CODE'), primary_key=True, index=True)
    DEP_ID: Mapped[str] = mapped_column(primary_key=True, index=True)
    DEP_NAME: Mapped[str] = mapped_column()

    course: Mapped["School"] = relationship(back_populates="departments")

    def __repr__(self):
        return f"<Department SCHL_CODE={self.SCHL_CODE}, DEP_ID={self.DEP_ID}, DEP_NAME={self.DEP_NAME})>"
    
class Course(Base):
    __tablename__ = 'courses'
    CRS_ID: Mapped[str] = mapped_column(primary_key=True, index=True)
    DEP_ID: Mapped[str] = mapped_column(ForeignKey('departments.DEP_ID'), index=True)
    CRS_NUM: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_CODE: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_NAME: Mapped[str] = mapped_column(nullable=False)
    CRS_DESC: Mapped[str] = mapped_column(nullable=False)
    CRS_GEAF: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_GEGH: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_DCOREL: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_UNITSTR: Mapped[str] = mapped_column(nullable=False)
    CRS_UNITS: Mapped[int] = mapped_column(index=True, nullable=False)
    CRS_PREREQ: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_COREQ: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_CROSS: Mapped[str] = mapped_column(index=True, nullable=False)
    CRS_NOTE: Mapped[str] = mapped_column(nullable=False)
    CRS_STARTTERM: Mapped[str] = mapped_column() # index=True, nullable=False
    CRS_ENDTERM: Mapped[str] = mapped_column() # index=True, nullable=False