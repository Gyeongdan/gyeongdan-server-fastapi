import os
from dataclasses import dataclass
from enum import Enum

from app.utils.async_file_operations import read_file_async


class Role(Enum):
    SIMPLE_ARTICLE = "simple_article"


@dataclass
class PromptInfo:
    version: str
    role: Role


class PromptVersion(Enum):
    V_2024_06_30 = PromptInfo(version="2024-06-30", role=Role.SIMPLE_ARTICLE)

    def get_system_prompt_path(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(
            base_dir,
            f"{self.value.role.value}/{self.value.version}.txt",
        )


async def get_system_prompt(version: PromptVersion):
    system_prompt_path = version.get_system_prompt_path()
    return await read_file_async(system_prompt_path)
