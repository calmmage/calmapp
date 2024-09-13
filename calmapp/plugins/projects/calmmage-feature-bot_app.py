from dataclasses import dataclass
from textwrap import dedent
from typing import List

from calmapp.app import App
from calmlib.utils.common import is_subsequence


class ShowcaseApp(App):
    features = [
        FeatureDescription(
            name="Whisper",
            description="The whisper plugin enables parsing of the audio messages into text",
            command="/showcase_whisper",
            project="t.me/calmmage_whisper_bot",
        ),
        FeatureDescription(
            name="Dummy",
            description="The dummy plugin is a placeholder for testing purposes",
            command="/showcase_dummy",
            project="t.me/calmmage_dummy_bot",
        ),
    ]

    # def __init__(self, features: List[FeatureDescription], plugins=None):
    def __init__(self, plugins=None):
        # self.features = features
        self._features_dict = {
            feature.name.lower(): feature for feature in self.features
        }
        super().__init__(plugins=plugins)

        # todo: move this check and propetry to base class
        # check if all plugins in required_plugins are present
        for plugin_name in self.required_plugins:
            if plugin_name not in self.plugins:
                raise AttributeError(
                    f"Plugin {plugin_name} is required but not found"
                    f"To enable the plugin set ENABLE_{plugin_name.upper()}=1 in the environment"
                )

        # todo: build embeddings for searching the ... features
        # alternative: ask chatgpt to do the search for us

    help_message = dedent(
        """
        Showcase bot features the commands demonstrating the features of the calmmage bot-lib.
        """
    )

    def get_help_message(self):
        message = super().get_help_message()
        message += "\n"
        message += self.get_info_message()
        return message

    def get_info_message(self):
        res = "Features:\n"
        for feature in self.features:
            description_first_line = feature.description.strip().split("\n")[0]
            res += f"{feature.command}: {description_first_line}\n"
        return res

    def get_start_message(self):
        message = dedent(
            """
            Hello! I am a showcase bot for the calmmage bot-lib. 
            I can show you commands based on the features of the bot-lib.
            """
        )
        message += "\n"
        message += self.get_info_message()
        return message

    # region Feature search
    def find_feature(self, feature: str, threshold=0.3) -> str:
        """
        Do a fuzzy embed search for the feature
        Returns a list of possible features that could match the result
         above the threshold probability
        """
        if feature in self._features_dict:
            return feature
        features = self._find_matching_features(feature, threshold)
        if len(features) == 0:
            raise ValueError(f"Feature {feature} not found")
        if len(features) > 1:
            raise ValueError(f"Multiple features found: {features}")
        return features[0]

    def _find_matching_features(self, feature: str, threshold=0.3) -> List[str]:
        """
        Do a fuzzy embed search for the feature
        Returns a list of possible features that could match the result
         above the threshold probability
        """
        # for now let's just do
        #  a) key is_substring of the name
        #  b) key in in the description
        results = []
        feature = feature.lower()
        for feature_name, feature_desc in self._features_dict.items():
            if (
                is_subsequence(feature, feature_name.lower())
                or feature in feature_desc.description.lower()
            ):
                results.append(feature_name)
        # todo: replace with proper fancy embedding search
        return results

    # endregion

    def get_feature(self, feature: str):
        """
        Get a feature by exact key
        """
        if feature not in self._features_dict:
            feature = self.find_feature(feature)
        return self._features_dict[feature]

    def describe_feature(self, feature: str):
        """
        describe a feature by exact key
        """
        if feature not in self._features_dict:
            feature = self.find_feature(feature)
        feature_description = self._features_dict[feature]
        message = dedent(
            """{name}
    
        Description
            {description}
        Showcase commands
            {command}
        Project
            {project}
        """
        )
        return message.format(
            name=feature_description.name,
            description=feature_description.description,
            command=feature_description.command,
            project=feature_description.project,
        )

    def dummy_feature(self, **kwargs):
        return f"Dummy feature. Got kwargs: {kwargs}"

    # region databases

    required_plugins = []
    # required_plugins = ["database"]

    def _init_databases(self):
        # todo: use self app config
        from dotenv import load_dotenv

        load_dotenv()
        # part 1 - private url, for securely storing user credentials and stuff

        # part 2 - public url, for data i need for other projects
        #  - e.g. logs, message history etc.

    # endregion databases

    def get_user_timezone(self, user_id):
        # if in database - just extract
        # if not - go request
        raise NotImplementedError

    def get_user_time(self, user_id):
        timezone = self.get_user_timezone(user_id)
        # get current time in the user's timezone
        raise NotImplementedError

    # region new features - 1 Jun 2024

    # endregion new features - 1 Jun 2024


class TimezoneError(Exception):
    pass


@dataclass
class FeatureDescription:
    """Dataclass for storing information about features of the calmmage bot-lib

    Attributes:
        name (str): Name of the feature
        description (str): Description of the feature
        command (str): Command to invoke the feature
        project (str): Link to the project where the feature is used and showcased more

    Example:
        name: str = "Whisper Plugin"
        description: str = "The whisper plugin enables parsing of the audio messages into text"
        command: str = "/showcase_whisper"
        project: str = "t.me/calmmage_whisper_bot"
    """

    name: str
    description: str
    command: str
    project: str

    def __str__(self):
        return f"{self.name}: {self.description} ({self.command})"

    def _validate(self):
        assert self.name, "Name is required"
        assert self.description, "Description is required"
        assert self.command.startswith("/"), "Command must start with /"
        # check project is a proper URL
        assert self.project.startswith("http"), "Project must be a valid URL"
