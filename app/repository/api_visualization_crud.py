# api_visualization_crud.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repository import get_repository, model_to_dict
from app.model.api_visualization import ApiVisualization


class ApiVisualizationRepository:
    # 생성
    async def create(self, api_article: ApiVisualization, session: AsyncSession):
        repository = get_repository(ApiVisualization)(session)
        return await repository.create(model_to_dict(api_article))

    async def get_by_id(self, pk: int, session: AsyncSession):
        repository = get_repository(ApiVisualization)(session)
        content = await repository.get(pk)
        if content is None:
            raise HTTPException(
                status_code=404, detail="해당 순번이 존재하지 않습니다."
            )
        return content

    async def get_all(self, session: AsyncSession):
        repository = get_repository(ApiVisualization)(session)
        return await repository.filter()

    async def update_content(self, id: int, content: str, session: AsyncSession):
        repository = get_repository(ApiVisualization)(session)
        return await repository.update_by_pk(pk=id, data={content: content})

    async def update_graph(self, id: int, graph_html: str, session: AsyncSession):
        repository = get_repository(ApiVisualization)(session)
        return await repository.update_by_pk(pk=id, data={graph_html: graph_html})
