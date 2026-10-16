from pydantic import BaseModel, Field
from typing import Literal


AlgorithmName = Literal[
    "logistic_regression",
    "decision_tree",
    "random_forest",
    "linear_regression",
    "ridge",
]


class TrainRequest(BaseModel):
    task: Literal["classification", "regression"]
    algorithm: AlgorithmName
    features: list[list[float]] = Field(min_length=4)
    targets: list[float | int] = Field(min_length=4)
    model_name: str = Field(default="model.joblib", pattern=r"^[A-Za-z0-9_.-]+$")


class PredictRequest(BaseModel):
    model_name: str = Field(pattern=r"^[A-Za-z0-9_.-]+$")
    features: list[list[float]] = Field(min_length=1)


class TrainResponse(BaseModel):
    status: str
    task: str
    algorithm: str
    model_name: str
    metrics: dict[str, float | int]


class PredictResponse(BaseModel):
    model_name: str
    predictions: list[float | int]
