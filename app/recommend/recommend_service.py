# pylint: disable=missing-module-docstring, missing-module-docstring, attribute-defined-outside-init, unnecessary-comprehension, not-callable, consider-using-f-string, unused-variable

import os

from scipy.sparse import csr_matrix
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.crawled_article import Articles
from app.model.user_type import UserTypes
from app.repository.recommend_crud import RecommendRepository
from app.service.article_manage_service import ArticleManageService
from app.repository.interaction_crud import InteractionRepository
from app.model.interaction import Interaction

import implicit

from app.service.user_type_service import UserTypeService


async def user_id_to_classification_id(user_id, session:AsyncSession) -> int:
    userType = await UserTypeService().get_user_type_by_id(user_id, session)
    target_features = [[userType.user_type_issue_finder, UserTypes.ISSUE_FINDER],
                       [userType.user_type_lifestyle_consumer, UserTypes.LIFESTYLE_CONSUMER],
                       [userType.user_type_entertainer, UserTypes.ENTERTAINER],
                       [userType.user_type_tech_specialist, UserTypes.TECH_SPECIALIST],
                       [userType.user_type_professionals, UserTypes.PROFESSIONALS]]
    target_features.sort(key=lambda x: x[0], reverse=True)
    data = {
        'classification_id': range(1, 11),
        'ISSUE_FINDER':         [1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        'LIFESTYLE_CONSUMER':   [1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
        'ENTERTAINER':          [1, 0, 0, 1, 1, 0, 1, 1, 0, 1],
        'TECH_SPECIALIST':      [0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
        'PROFESSIONALS':        [0, 0, 1, 0, 1, 1, 0, 1, 1, 1]
    }
    df = pd.DataFrame(data)
    filtered_df = df[
        (df[target_features[0][1].value['name']] == 1) &
        (df[target_features[1][1].value['name']] == 1) &
        (df[target_features[2][1].value['name']] == 1)
        ]
    return (int)(filtered_df.iloc[0]['classification_id'])

def articles_to_dataframe(articles: list[Articles]) -> pd.DataFrame:
    # 객체 리스트를 딕셔너리 리스트로 변환
    articles_dict_list = [
        {
            "article_id": article.id,
            'ECONOMY_AND_BUSINESS': 0,
            'POLITICS_AND_SOCIETY': 0,
            'SPORTS_AND_LEISURE': 0,
            'TECHNOLOGY_AND_CULTURE': 0
            # "created_at": article.created_at.strftime('%Y-%m-%d'),
        }
        for article in articles
    ]
    for i in range(len(articles_dict_list)):
        articles_dict_list[i][articles[i].category] = 1

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

class RecommendService:
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.interaction_datas = None
        self.classification_datas = None
        self.num_classifications = None
        self.num_articles = None
        self.user_item_matrix = None
        self.model = None
        self.idx_to_id = dict()
        self.id_to_idx = dict()
        self.user_data_path = "/./user_classification.csv"

    async def initialize_data(self, session):
        self.set_user_datas()
        await self.set_article_datas(session)
        await self.set_interaction_datas(session)

    def set_user_datas(self):
        self.classification_datas = pd.read_csv(os.path.dirname(os.path.abspath(__file__)) + self.user_data_path)
        self.num_classifications = len(self.classification_datas)
        print(self.num_classifications)

    async def set_article_datas(self, session):

        articles = await ArticleManageService().get_all_articles(session=session)
        for idx, article in enumerate(articles):
            self.idx_to_id[idx] = article.id
            self.id_to_idx[article.id] = idx
        self.num_articles = len(articles)
        print(self.num_articles)

    async def set_interaction_datas(self, session):
        interactions = await InteractionRepository().get_all(session=session)
        self.interaction_datas = interaction_to_dataframe(interactions)

    def make_dataset(self):
        print(self.interaction_datas)
        self.user_item_matrix = csr_matrix((self.interaction_datas['duration_time'].tolist(),
                    (self.interaction_datas['classification_id'].tolist(),
                     list(map(lambda x : self.id_to_idx[x], self.interaction_datas['article_id'].tolist()))))
                                           , shape=(self.num_classifications+1, self.num_articles))

        self.user_item_matrix = (self.user_item_matrix > 0).astype(np.float32)
        print("Num users: {}, num_items {}.".format(self.num_classifications, self.num_articles))

    def make_model(
        self,
        factors: int = 5,
        regulartization: float = 0.1,
        iterations: int = 20
    ):
        self.model = implicit.als.AlternatingLeastSquares(factors=factors,
                                                          regularization=regulartization,
                                                          iterations=iterations)

    def fit_model(self):
        self.make_dataset()
        self.make_model()
        self.model.fit(
            self.user_item_matrix
        )

    async def get_recommend_articles(self, classification_id: int, session: AsyncSession, N: int = 10):
        indices, scores = self.model.recommend(userid=classification_id, user_items=csr_matrix(self.user_item_matrix.toarray()[classification_id]), N=N)
        for i in range(N):
            indices[i] = self.idx_to_id[indices[i]]

        await RecommendRepository().update_recommend(id=classification_id+1, article_ids=indices, session=session)

        return indices


    def add_interaction_data(self, classification_id: int, article_id: int, duration_time:int = 1):
        InteractionRepository().create(
            Interaction(
                classification_id=classification_id,
                article_id=article_id,
                duration_time=duration_time
            )
        )
