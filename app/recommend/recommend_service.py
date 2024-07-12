# pylint: disable=missing-module-docstring, missing-module-docstring, attribute-defined-outside-init, unnecessary-comprehension, not-callable, consider-using-f-string, unused-variable

import asyncio
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from fastapi import Depends

from app.database.repository import model_to_dict
from app.database.session import get_db_session
from app.model.crawled_article import Articles
from app.service.article_manage_service import ArticleManageService
from app.repository.interaction_crud import InteractionRepository
from app.model.interaction import Interaction
from lightfm import LightFM
from lightfm.data import Dataset  # pylint: disable=E0611

warnings.filterwarnings("ignore")


def articles_to_dataframe(articles: list[Articles]) -> pd.DataFrame:
    # 객체 리스트를 딕셔너리 리스트로 변환
    articles_dict_list = [
        {
            "article_id": article.id,
            article.category: 1,
            # "created_at": article.created_at.strftime('%Y-%m-%d'),
        }
        for article in articles
    ]

    df = pd.DataFrame(articles_dict_list)
    return df

def interaction_to_dataframe(interactions : list[Interaction]) -> pd.DataFrame:
    interaction_dict_list = [
        {
            "classification_id": interaction.classification_id,
            "article_id": interaction.article_id,
            "duration_time": interaction.duration_time
        }
        for interaction in interactions
    ]
    df = pd.DataFrame(interaction_dict_list)
    return df

class ArticleDataInfo:
    def __init__(self, article_id, category, created_at):
        self.article_data = pd.DataFrame(
            {
                "article_id": article_id,
                "경제 및 기업": [0],
                "정치 및 사회": [0],
                "기술 및 문화": [0],
                "스포츠 및 여가": [0],
                "오피니언 및 분석": [0],
                # "created_at": [created_at],
            }
        )
        self.article_data.iloc[0][category] = 1


class InteractionDataInfo:
    def __init__(self, user_id, article_id, duration_time):
        self.interaction_data = pd.DataFrame(
            {
                "classification_id": [user_id],
                "article_id": [article_id],
                "duration_time": [duration_time],
            }
        )


class RecommendService:
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.interaction_datas = None

    def set_user_datas(self, user_data_path):
        self.user_data_path = user_data_path
        self.user_datas = pd.read_csv(user_data_path)

    async def initialize_data(self, session):
        self.set_user_datas("app/recommend/user_classification.csv")
        await self.set_article_datas(session)
        await self.set_interaction_datas(session)

    async def set_article_datas(self, session):
        # session = Depends(get_db_session)
        articles = await ArticleManageService().get_all_articles(session=session)
        self.article_datas = pd.get_dummies(articles_to_dataframe(articles))

    async def set_interaction_datas(self, session):
        # session = Depends(get_db_session)
        interactions = await InteractionRepository().get_all(session=session)
        self.interaction_datas = interaction_to_dataframe(interactions)
        print(self.interaction_datas.columns)

    def make_dataset(self):
        self.user_datas = pd.get_dummies(self.user_datas)
        self.user_features_col = self.user_datas.drop(
            columns=["classification_id"]
        ).columns.values
        self.user_feat = self.user_datas.drop(columns=["classification_id"]).to_dict(
            orient="records"
        )

        self.item_features = self.article_datas
        self.item_features_col = self.item_features.drop(
            columns=["article_id"]
        ).columns.values
        self.item_feat = self.item_features.drop(
            columns=["article_id"]
        ).to_dict(orient="records")

        self.dataset = Dataset()
        self.dataset.fit(
            users=[x for x in self.user_datas["classification_id"]],
            items=[x for x in self.article_datas["article_id"]],
            item_features=self.item_features_col,
            user_features=self.user_features_col,
        )

        self.item_features = self.dataset.build_item_features(
            (x, y) for x, y in zip(self.item_features["article_id"], self.item_feat)
        )
        self.user_features = self.dataset.build_user_features(
            (x, y) for x, y in zip(self.user_datas["classification_id"], self.user_feat)
        )

        (self.interactions, self.weights) = self.dataset.build_interactions(
            (x, y, z)
            for x, y, z in zip(
                self.interaction_datas["classification_id"],
                self.interaction_datas["article_id"],
                self.interaction_datas["duration_time"],
            )
        )

        num_users, num_items = self.dataset.interactions_shape()
        print("Num users: {}, num_items {}.".format(num_users, num_items))

    def make_model(
        self,
        n_components: int = 30,
        loss: str = "warp",
        epoch: int = 30,
        num_thread: int = 4,
    ):
        self.n_components = n_components
        self.loss = loss
        self.epoch = epoch
        self.num_thread = num_thread
        self.model = LightFM(
            no_components=self.n_components, loss=self.loss, random_state=1616
        )

    def fit_model(self):
        self.make_dataset()
        self.make_model()
        self.model.fit(
            self.interactions,
            user_features=self.user_features,
            item_features=self.item_features,
            epochs=self.epoch,
            num_threads=self.num_thread,
            sample_weight=self.weights,
        )

    def get_top_n_articles(self, user_id: int, article_num: int):
        item_ids = np.arange(self.interactions.shape[1])  # 예측할 아이템 ID 배열

        predictions = self.model.predict(user_id, item_ids)
        top_items = self.article_datas.iloc[np.argsort(-predictions)[:article_num]]
        return top_items

    def similar_items(self, item_id, N=10):
        item_bias, item_representations = self.model.get_item_representations(
            features=self.item_features
        )

        scores = item_representations.dot(item_representations[item_id, :])
        best = np.argpartition(scores, -N)[-N:]

        return self.article_datas.iloc[best]

    def get_classification_for_article(self, article_id:id):
        scores = self.model.predict(np.arange(len(self.user_datas)), np.full(len(self.user_datas), article_id))
        top_users = np.argsort(-scores)

        score_for_classification = [0 for _ in range(5)]
        weight = 10
        for user_id in top_users[:10]:
            for i in range(5):
                score_for_classification[i] += self.user_datas.iloc[user_id][self.user_datas.columns[i+2]] * (2 ** weight)
            weight -= 1

        total = sum(score_for_classification)
        for i in range(5):
            score_for_classification[i] = (int)( score_for_classification[i] / (total /100))

        return score_for_classification

    def get_time_weight(self, article_id):
        today = datetime.now().date()
        date_obj = datetime.strptime(
            self.article_datas[self.article_datas["article_id"] == article_id][
                "created_at"
            ].iloc[0],
            "%Y-%m-%d",
        ).date()
        difference = today - date_obj
        return max(1 - ((difference.days // 30) / 5), 0)

    def fit_model_partialy(self):
        self.make_dataset()
        self.model.fit_partial(self.interactions, item_features=self.item_features)

    def add_interaction_data(self, interaction_data: InteractionDataInfo):
        InteractionRepository().create(
            Interaction(
                classification_id=interaction_data.interaction_data['classification_id'],
                article_id=interaction_data.interaction_data['article_id'],
                duration_time=interaction_data.interaction_data['duration_time']
            )
        )