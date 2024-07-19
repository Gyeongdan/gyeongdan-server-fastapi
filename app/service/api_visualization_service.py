# api_visualization_router.py
# pylint: disable=R0911
# pylint: disable=C0206
# pylint: disable=C0327
import json
from enum import Enum
from typing import List

import pandas as pd
import plotly.express as px
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.repository.api_visualization_crud import (
    ApiVisualization,
    ApiVisualizationRepository,
)
from app.service.public_data_api_service import PublicDataAPI, PublicDataAPIService
from app.utils.json_parser import parse


# data의 이름이 다를 때 관리하는 class
class APIDataEnum(Enum):
    JINJU_COVID = ("진주 코비드", "data")
    SKELETON = ("???", "skeleton")

    @classmethod
    def get_variable(cls, api_data_value):
        for item in cls:
            if item.value[0] == api_data_value:
                return item.value[1]
        raise ValueError(f"No matching variable for API data value: {api_data_value}")


# 기본적인 친구들
class ApiVisualizationService:
    async def create_article(
        self, title: str, content: str, graph_html: str, session: AsyncSession
    ) -> ApiVisualization:
        return await ApiVisualizationRepository().create(
            api_article=ApiVisualization(
                title=title, content=content, graph_html=graph_html
            ),
            session=session,
        )

    async def get_by_id(self, id: int, session: AsyncSession) -> ApiVisualization:
        return await ApiVisualizationRepository().get_by_id(pk=id, session=session)

    async def get_all(self, session: AsyncSession) -> List[ApiVisualization]:
        return await ApiVisualizationRepository().get_all(session=session)

    async def update_content(self, id: int, content: str, session: AsyncSession):
        return await ApiVisualizationRepository().update_content(
            content=content, id=id, session=session
        )

    async def update_graph(self, id: int, graph_html: str, session: AsyncSession):
        return await ApiVisualizationRepository().update_graph(
            id=id, graph_html=graph_html, session=session
        )


class GraphService:
    # dataset을 기본으로 가지고 있는 class입니다.
    def __init__(self, dataset=None):
        self.dataset = dataset
        # 함수가 외부에서 들어온 함수를 사용합니다. 그래서 위험할 수 있어서 safe 부분을 만듭니다.
        # 넓이와 높이는 아예 고정으로 갈 수도 있으니 생각하기
        # barmode for bar
        self.safe_plotly_kwargs = {
            "title",
            "color",
            "labels",
            "barmode",
            "template",
            "width",
            "height",
            "text_auto",
            "text",
            "hover_data",
            "animation_frame",
            "animation_group",
            "size",
            "symbol",
            "trendline",
            "histfunc",
            "markers",
            "geojson",
            "featureidkey",
            "hover_name",
            "color_continuous_scale",
            "fitbounds",
        }
        self.safe_pandas_params = {
            "melt": {"id_vars", "value_vars"},
            "pivot": {"index", "columns", "values"},
            # 이걸 할 수가 있나? .agg로 받아야 할 텐데..
            "groupby": {"by", "agg_func"},
            # 이것도 살짝 이해가 안되네
            "filter": {"condition"},
            "drop": {"columns", "index"},
            # fillna는 쓸 일 없을 듯 하니 제거
            "replace": {"to_replace", "value"},
            "merge": {"on", "how"},
            "sort": {"by", "ascending"},
            "reset_index": {},
        }

    # 그래프 그리는 함수
    async def plot_graph(self, graph_type, x, y, preprocessing_steps=None, **kwargs):
        # 원본 데이터를 건드리지 않으려고 변수를 사용합니다.
        df = self.dataset

        # 전처리 과정
        if preprocessing_steps:
            df = await self.apply_preprocessing(df, preprocessing_steps)

        # 그래프 종류는 우선 5가지로 정했습니다.
        # 확장과 수정이 용이하게 적었습니다.
        new_kwargs = {}
        for graph_material in kwargs:
            if graph_material in self.safe_plotly_kwargs:
                new_kwargs[graph_material] = kwargs[graph_material]
        if graph_type == "bar":
            return await self.plot_bar(df, x, y, **new_kwargs)
        if graph_type == "line":
            return await self.plot_line(df, x, y, **new_kwargs)
        if graph_type == "pie":
            return await self.plot_pie(df, x, y, **new_kwargs)
        if graph_type == "histogram":
            return await self.plot_histogram(df, x, None, **new_kwargs)
        if graph_type == "scatter":
            return await self.plot_scatter(df, x, y, **new_kwargs)
        if graph_type == "choropleth":
            return await self.plot_choropleth(df, x, y, **new_kwargs)
        if graph_type == "funnel":
            return await self.plot_funnel(df, x, y, **new_kwargs)

    # 전처리 작업이 필요한 경우 사용합니다.
    async def apply_preprocessing(self, df, steps):
        for step in steps:
            step_type = step.get("type")
            params = step.get("params", {})
            # 허용된 친구들만 사용!!!!
            if step_type in self.safe_pandas_params:
                filtered_params = {
                    k: v
                    for k, v in params.items()
                    if k in self.safe_pandas_params[step_type]
                }
                # 비어있으면 제끼기
                if not filtered_params:
                    continue
            if step_type == "melt":
                df = await self.preprocess_melt(df, **filtered_params)
            elif step_type == "pivot":
                df = await self.preprocess_pivot(df, **filtered_params)
            elif step_type == "groupby":
                df = await self.preprocess_groupby(df, **filtered_params)
            elif step_type == "filter":
                df = await self.preprocess_filter(df, **filtered_params)
            elif step_type == "drop":
                df = await self.preprocess_drop(df, **filtered_params)
            elif step_type == "replace":
                df = await self.preprocess_replace(df, **filtered_params)
            elif step_type == "merge":
                df = await self.preprocess_merge(df, **filtered_params)
            elif step_type == "sort":
                df = await self.preprocess_sort(df, **filtered_params)
            else:
                raise ValueError(f"Invalid preprocessing step: {step_type}")
        return df

    # 그래프 그리기 함수들
    async def plot_bar(self, df, x, y, **kwargs):
        if "text" not in kwargs:
            kwargs["text_auto"] = True

        fig = px.bar(df, x=x, y=y, **kwargs)
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if "animation_frame" in kwargs:
            fig["layout"].pop("updatemenus")
        return fig

    async def plot_line(self, df, x, y, **kwargs):
        fig = px.line(df, x=x, y=y, **kwargs)
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if "animation_frame" in kwargs:
            fig["layout"].pop("updatemenus")
        return fig

    async def plot_pie(self, df, names, values, **kwargs):
        fig = px.pie(df, names=names, values=values, **kwargs)
        return fig

    # 통일성을 위해 y를 주긴 하지만, 사용하지 않습니다.
    async def plot_histogram(self, df, x, y=None, **kwargs):
        fig = px.histogram(df, x=x, y=y, **kwargs)
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if "animation_frame" in kwargs:
            fig["layout"].pop("updatemenus")
        return fig

    async def plot_scatter(self, df, x, y, **kwargs):
        fig = px.scatter(df, x=x, y=y, **kwargs)
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if "animation_frame" in kwargs:
            fig["layout"].pop("updatemenus")

        return fig

    async def plot_choropleth(self, df, locations, color, **kwargs):
        fig = px.choropleth(data_frame=df, locations=locations, color=color, **kwargs)

        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if "animation_frame" in kwargs:
            fig["layout"].pop("updatemenus")

        # 안보일 수 있어서 보이게 하는 친구
        fig.update_geos(fitbounds="locations", visible=False)

        return fig

    async def plot_funnel(self, df, x, y, **kwargs):
        fig = px.funnel(data_frame=df, x=x, y=y, **kwargs)

        if "animation_frame" in kwargs:
            fig["layout"].pop("updatemenus")

        return fig

    # 전처리 함수들
    async def preprocess_melt(self, df, id_vars, value_vars):
        return pd.melt(df, id_vars=id_vars, value_vars=value_vars)

    async def preprocess_pivot(self, df, index, columns, values):
        return df.pivot(index=index, columns=columns, values=values)

    async def preprocess_groupby(self, df, by, agg_func):
        return df.groupby(by).agg(agg_func).reset_index()

    async def preprocess_filter(self, df, condition):
        return df.query(condition)

    async def preprocess_drop(self, df, columns=None, index=None):
        return df.drop(columns=columns, index=index)

    async def preprocess_replace(self, df, to_replace, value):
        return df.replace(to_replace, value)

    async def preprocess_merge(self, df1, df2, on, how="inner"):
        return df1.merge(df2, on=on, how=how)

    async def preprocess_sort(self, df, by, ascending=True):
        return df.sort_values(by=by, ascending=ascending)

    # col 가져오기
    async def show_col(self):
        # head를 넘겨주자.
        return [self.dataset.columns.tolist()] + self.dataset.head().values.tolist()

    # session을 쓸 수도 있어서 남겨 놓겠습니다!
    async def graph_info(
        self,
        title: str,
        summary=None,
        # session: AsyncSession
    ):
        ai_client = get_platform_client(LLMModel.OPENAI_GPT4o)

        # prompt
        system_prompt = await get_system_prompt(version=PromptVersion.V_2024_07_10)

        if summary is None:
            col_list = await self.show_col()
            # 수정
            request_text = "summary:" + str(col_list) + "\n" + "title:" + title

        else:
            request_text = summary + "\n" + title

        ai_result = parse(
            await ai_client.request(
                request_text=request_text,
                system_prompt=system_prompt,
                assistant_prompt=None,
                model=LLMModel.OPENAI_GPT4o,
            )
        )

        return ai_result

    async def get_api_data(self, api_data):
        temp = PublicDataAPIService()
        data_in_list = parse(await temp.response(api_data))

        data_type = APIDataEnum.get_variable(api_data)
        df = pd.DataFrame(data_in_list[data_type])
        print(df)
        # 값을 가져오지 못했을 때를 위하여
        if df.empty:
            print("df가 제대로 없는 경우")
            return 0
        self.dataset = df
        return 1


async def create_article(
    title: str, data: PublicDataAPI, user_input: bool, session: AsyncSession
):
    graph_service = GraphService()
    if not await graph_service.get_api_data(data):
        raise HTTPException(status_code=400, detail="Couldn't get data")

    # 여기가 ai보고 데이터 받아오라고 하는 곳.
    ai_result = await graph_service.graph_info(title=title)
    # 전처리 완료
    await graph_service.apply_preprocessing(
        graph_service.dataset, ai_result["preprocessing_steps"]
    )

    # 그래프 그리는 부분
    # 근데 이 곳을 제끼고 return 을 달리하라는 거임.

    # fig = await graph_service.plot_graph(
    #     ai_result["graph_type"],
    #     ai_result["x_value"],
    #     ai_result["y_value"],
    #     ai_result["preprocessing_steps"],
    #     **ai_result["kwargs"],
    # )
    #
    # # html 다 만든 것
    # html_str = pio.to_html(fig, full_html=True)

    x = graph_service.dataset[ai_result["x_value"]].tolist()
    y = graph_service.dataset[ai_result["y_value"]].tolist()
    graph_type = ai_result["graph_type"]
    # 우선 무슨 값을 넣을 지 몰라서 hard coding 합니다.
    mode = "lines+markers"
    marker = "{color: 'red'}"

    data = [{"x": x, "y": y, "type": graph_type, "mode": mode, "marker": marker}]

    layout = {"title": title}

    chart_config = {
        "data": data,
        "layout": layout,
    }

    json_data = json.dumps(chart_config, ensure_ascii=False)
    if user_input:
        # 유저의 통제시 그냥 html만 리턴!
        return json_data, ""
        # 기사를 만드는 경우는 저장을 한다!
    repository = ApiVisualizationService()
    await repository.create_article(
        title=title,
        graph_html=json.dumps(chart_config),
        content=ai_result["article"]["body"],
        session=session,
    )
    return json_data, ai_result["article"]["body"]
