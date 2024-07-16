from enum import Enum

from sqlalchemy import BigInteger, Column, Integer, Text

from app.database.repository import Base


class UserType(Base):
    __tablename__ = "user_type"
    __table_args__ = {"schema": "gyeongdan"}

    user_id = Column(BigInteger, primary_key=True, index=True)
    user_type_issue_finder = Column(Integer, nullable=True)
    user_type_lifestyle_consumer = Column(Integer, nullable=True)
    user_type_entertainer = Column(Integer, nullable=True)
    user_type_tech_specialist = Column(Integer, nullable=True)
    user_type_professionals = Column(Integer, nullable=True)
    user_type = Column(Text, nullable=True)


class UserTypes(Enum):
    NONE= {'id':-1,
           'name':'NONE'
           }
    ISSUE_FINDER= {'id':0,
                   'name':'ISSUE_FINDER'}
    LIFESTYLE_CONSUMER= {'id':1,
                         'name':'LIFESTYLE_CONSUMER'}
    ENTERTAINER= {'id':2,
                  'name':'ENTERTAINER'}
    TECH_SEPCIALIST= {'id':3,
                      'name':'TECH_SEPCIALIST'}
    PROFESSIONALS= {'id':4,
                    'name':'PROFESSIONALS'}
