"""验证码适配器接口"""

from dataclasses import dataclass
from typing import Protocol

from .data_model import GeetestResult


@dataclass
class CaptchaTask:
    """验证码任务上下文"""
    gt: str
    challenge: str
    url: str = ""
    raw: dict | None = None


class CaptchaSolver(Protocol):
    """验证码解算器接口"""

    name: str

    def solve(self, task: CaptchaTask) -> GeetestResult:
        ...
