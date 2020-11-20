import os
import glob

from typing import List

from .settings import ModelParameters, ModelSettings

DEFAULT_MODEL_SETTINGS_FILENAME = "model-settings.json"


class ModelSettingsLoader:
    """
    Class responsible for loading model settings from the file system.
    """

    def __init__(self, root: str = None):
        self._root = root

    def list(self) -> List[ModelSettings]:
        all_model_settings = []

        if self._root:
            pattern = os.path.join(self._root, "**", DEFAULT_MODEL_SETTINGS_FILENAME)
            matches = glob.glob(pattern, recursive=True)

            for model_settings_path in matches:
                model_settings = self._load_model_settings(model_settings_path)
                all_model_settings.append(model_settings)

        # If there were no matches, try to load model from environment
        if not all_model_settings:
            # return default
            model_settings = ModelSettings()
            model_settings.parameters = ModelParameters()
            all_model_settings.append(model_settings)

        return all_model_settings

    def _load_model_settings(self, model_settings_path: str) -> ModelSettings:
        model_settings = ModelSettings.parse_file(model_settings_path)

        if not model_settings.parameters:
            model_settings.parameters = ModelParameters()

        if not model_settings.parameters.uri:
            # If not specified, default to its own folder
            default_model_uri = os.path.dirname(model_settings_path)
            model_settings.parameters.uri = default_model_uri

        return model_settings

    def read(self, name: str) -> ModelSettings:
        pass
