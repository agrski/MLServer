import json
import pytest
import os
import shutil

from mlserver.handlers import DataPlane
from mlserver.repository import MultiModelRepository
from mlserver.loader import ModelSettingsLoader, DEFAULT_MODEL_SETTINGS_FILENAME
from mlserver import types, Settings, ModelSettings

from .fixtures import SumModel
from .helpers import get_import_path

TESTS_PATH = os.path.dirname(__file__)
TESTDATA_PATH = os.path.join(TESTS_PATH, "testdata")


def pytest_collection_modifyitems(items):
    """
    Add pytest.mark.asyncio marker to every test.
    """
    for item in items:
        item.add_marker("asyncio")


@pytest.fixture
def sum_model_settings() -> ModelSettings:
    model_settings_path = os.path.join(TESTDATA_PATH, "model-settings.json")
    return ModelSettings.parse_file(model_settings_path)


@pytest.fixture
def sum_model(sum_model_settings: ModelSettings) -> SumModel:
    return SumModel(settings=sum_model_settings)


@pytest.fixture
def metadata_server_response() -> types.MetadataServerResponse:
    payload_path = os.path.join(TESTDATA_PATH, "metadata-server-response.json")
    return types.MetadataServerResponse.parse_file(payload_path)


@pytest.fixture
def metadata_model_response() -> types.MetadataModelResponse:
    payload_path = os.path.join(TESTDATA_PATH, "metadata-model-response.json")
    return types.MetadataModelResponse.parse_file(payload_path)


@pytest.fixture
def inference_request() -> types.InferenceRequest:
    payload_path = os.path.join(TESTDATA_PATH, "inference-request.json")
    return types.InferenceRequest.parse_file(payload_path)


@pytest.fixture
def inference_response() -> types.InferenceResponse:
    payload_path = os.path.join(TESTDATA_PATH, "inference-response.json")
    return types.InferenceResponse.parse_file(payload_path)


@pytest.fixture
async def model_repository(sum_model: SumModel) -> MultiModelRepository:
    model_repository = MultiModelRepository()
    await model_repository.load(sum_model)
    return model_repository


@pytest.fixture
def settings() -> Settings:
    settings_path = os.path.join(TESTDATA_PATH, "settings.json")
    return Settings.parse_file(settings_path)


@pytest.fixture
def data_plane(settings: Settings, model_repository: MultiModelRepository) -> DataPlane:
    return DataPlane(settings=settings, model_repository=model_repository)


@pytest.fixture
def model_folder(tmp_path):
    to_copy = ["model-settings.json"]

    for file_name in to_copy:
        src = os.path.join(TESTDATA_PATH, file_name)
        dst = tmp_path.joinpath(file_name)
        shutil.copyfile(src, dst)

    return tmp_path


@pytest.fixture
def multi_model_folder(model_folder, sum_model_settings):
    # Remove original
    model_settings_path = os.path.join(model_folder, DEFAULT_MODEL_SETTINGS_FILENAME)
    os.remove(model_settings_path)

    num_models = 5
    for idx in range(num_models):
        sum_model_settings.parameters.version = f"v{idx}"

        model_version_folder = os.path.join(
            model_folder,
            "sum-model",
            sum_model_settings.parameters.version,
        )
        os.makedirs(model_version_folder)

        model_settings_path = os.path.join(
            model_version_folder, DEFAULT_MODEL_SETTINGS_FILENAME
        )
        with open(model_settings_path, "w") as f:
            settings_dict = sum_model_settings.dict()
            settings_dict["implementation"] = get_import_path(
                sum_model_settings.implementation
            )
            f.write(json.dumps(settings_dict))

    return model_folder


@pytest.fixture
def model_settings_loader(model_folder):
    return ModelSettingsLoader(model_folder)
