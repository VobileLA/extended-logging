from enum import Enum


class LogFormat(Enum):
    JSON = "json"
    ECS = "ecs"
    BASIC = "basic"