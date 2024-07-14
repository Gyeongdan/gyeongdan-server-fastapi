# api_visualization_service.py
# pylint: disable=R0914

import pandas as pd
import plotly.express as px

from app.model.ai_client.ai_client import LLMModel
from app.model.ai_client.get_platform_client import get_platform_client
from app.model.prompt.prompt_version import PromptVersion, get_system_prompt
from app.utils.json_parser import parse

# from sqlalchemy.ext.asyncio import AsyncSession


class GraphService:
    # dataset을 기본으로 가지고 있는 class입니다.
    def __init__(self, dataset):
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
        }

    # 그래프 그리는 함수
    async def plot_graph(self, graph_type, x, y, preprocessing_steps=None, **kwargs):
        # 원본 데이터를 건드리지 않으려고 변수를 사용합니다.
        df = self.dataset

        # 전처리 과정
        if preprocessing_steps:
            df = await self.apply_preprocessing(df, preprocessing_steps)

        # 그래프 종류는 우선 5가지로 정했습니다.
        # 막대그래프, 선그래프, 원형 그래프, 히스토그램, 점산도 그래프
        # 확장과 수정이 용이하게 적었습니다.
        for graph_material in kwargs:
            if graph_material not in self.safe_plotly_kwargs:
                raise ValueError("Not safe type")
        if graph_type == "bar":
            return await self.plot_bar(df, x, y, **kwargs)
        if graph_type == "line":
            return await self.plot_line(df, x, y, **kwargs)
        if graph_type == "pie":
            return await self.plot_pie(df, x, y, **kwargs)
        if graph_type == "histogram":
            return await self.plot_histogram(df, x, None, **kwargs)
        if graph_type == "scatter":
            return await self.plot_scatter(df, x, y, **kwargs)

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
                print(filtered_params)
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
    async def plot_bar(
        self,
        df,
        x,
        y,
        title="",
        color=None,
        labels=None,
        template=None,
        width=800,
        height=600,
        barmode="relative",
        text_auto=False,
        text=None,
        hover_data=None,
        animation_frame=None,
        animation_group=None,
    ):
        if text is None:
            text_auto = True

        fig = px.bar(
            df,
            x=x,
            y=y,
            title=title,
            color=color,
            labels=labels,
            template=template,
            width=width,
            height=height,
            barmode=barmode,
            text_auto=text_auto,
            text=text,
            hover_data=hover_data,
            animation_frame=animation_frame,
            animation_group=animation_group,
        )
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if animation_frame is not None:
            fig["layout"].pop("updatemenus")
        return fig

    async def plot_line(
        self,
        df,
        x,
        y,
        title="",
        color=None,
        labels=None,
        template=None,
        width=800,
        height=600,
        markers=True,
        animation_frame=None,
        animation_group=None,
    ):
        fig = px.line(
            df,
            x=x,
            y=y,
            title=title,
            color=color,
            labels=labels,
            template=template,
            width=width,
            height=height,
            markers=markers,
            animation_frame=animation_frame,
            animation_group=animation_group,
        )
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if animation_frame is not None:
            fig["layout"].pop("updatemenus")
        return fig

    async def plot_pie(
        self,
        df,
        names,
        values,
        title="",
        color=None,
        labels=None,
        template=None,
        width=800,
        height=600,
        hover_data=None,
    ):
        fig = px.pie(
            df,
            names=names,
            values=values,
            title=title,
            color=color,
            labels=labels,
            template=template,
            width=width,
            height=height,
            hover_data=hover_data,
        )
        return fig

    # 통일성을 위해 y를 주긴 하지만, 사용하지 않습니다.
    async def plot_histogram(
        self,
        df,
        x,
        y=None,
        title="",
        color=None,
        labels=None,
        template=None,
        width=800,
        height=600,
        text_auto=True,
        histfunc=None,
        animation_frame=None,
        animation_group=None,
    ):
        fig = px.histogram(
            df,
            x=x,
            y=y,
            title=title,
            color=color,
            labels=labels,
            template=template,
            width=width,
            height=height,
            text_auto=text_auto,
            histfunc=histfunc,
            animation_frame=animation_frame,
            animation_group=animation_group,
        )
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if animation_frame is not None:
            fig["layout"].pop("updatemenus")
        return fig

    async def plot_scatter(
        self,
        df,
        x,
        y,
        title="",
        color=None,
        labels=None,
        template=None,
        width=800,
        height=600,
        hover_data=None,
        size=None,
        symbol=None,
        trendline=None,
        animation_frame=None,
        animation_group=None,
    ):
        fig = px.scatter(
            df,
            x=x,
            y=y,
            title=title,
            color=color,
            labels=labels,
            template=template,
            width=width,
            height=height,
            hover_data=hover_data,
            size=size,
            symbol=symbol,
            trendline=trendline,
            animation_frame=animation_frame,
            animation_group=animation_group,
        )
        # slider 값이 들어왔을 때, 애니메이션 버튼 없애주는 친구
        if animation_frame is not None:
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
        return list(self.dataset.columns)

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
            request_text = ",".join(col_list) + "\n" + title

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
