from fastapi import APIRouter
from src.api.v1.fine_tuning import router as fine_tuning_router
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router
from src.api.v1.history import router as history_router
from src.api.v1.files import router as files_router
from src.api.v1.deep_learning import router as deep_learning_router
from src.api.v1.mlops import router as mlops_router
from src.api.v1.model_registry import router as model_registry_router
from src.api.v1.monitoring import router as monitoring_router
from src.api.v1.machine_learning import router as machine_learning_router
from src.api.v1.csv_machine_learning import router as csv_machine_learning_router

from src.api.v1.traffic import router as traffic_router
from src.api.v1.vision import router as vision_router
from src.api.v1.speech import router as speech_router
from src.api.v1.translation import router as translation_router
from src.api.v1.multimodal import router as multimodal_router

from src.api.v1.health import router as health_router
from src.api.v1.dashboard import router as dashboard_router
from src.api.v1.rag import router as rag_router
from src.api.v1.knowledge_base import router as knowledge_base_router
from src.api.v1.vector_search import router as vector_search_router
from src.api.v1.agents import router as agents_router
from src.api.v1.automation import router as automation_router
from src.api.v1.prompts import router as prompts_router
from src.api.v1.llm import router as llm_router

api_router = APIRouter()

for module_router in (
    auth_router,
    users_router,
    monitoring_router,
    model_registry_router,
    mlops_router,
    deep_learning_router,
    files_router,
    history_router,
    traffic_router,
    vision_router,
    speech_router,
    translation_router,
    multimodal_router,
    health_router,
    dashboard_router,
    rag_router,
    knowledge_base_router,
    vector_search_router,
    agents_router,
    automation_router,
    prompts_router,
    llm_router,
    machine_learning_router,
    csv_machine_learning_router,
    fine_tuning_router,
):
    api_router.include_router(module_router)