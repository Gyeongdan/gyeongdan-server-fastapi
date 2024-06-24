from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db_session
from app.service.email_address_service import AddressService

address_router = APIRouter()


class UserCreateRequestDTO(BaseModel):
    name : str
    emailAddress : str

@address_router.post("/addresses/save")
async def create_user(
    name :str, emailAddress:str, session: AsyncSession = Depends(get_db_session)
):
    return await AddressService().create_address(emailAddress, name, session)



@address_router.get("/addresses/{id}")
async def get_user_data_by_id(id: int, session: AsyncSession = Depends(get_db_session)):
    return await AddressService().get_user_data_by_id(id, session)


@address_router.get("/addresses")
async def get_all_user_datas(session: AsyncSession = Depends(get_db_session)):
    return await AddressService().get_all_user_datas(session)
