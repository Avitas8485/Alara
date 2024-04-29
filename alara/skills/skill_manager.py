import importlib
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class NotImplementError(Exception):
    """Exception raised for errors in the input.
    Attributes:
        feature_name -- feature name that has not been implemented
        message -- explanation of the error"""

    def __init__(self, feature_name: str):
        self.feature_name = feature_name
        self.message = f"Feature {feature_name} has not been implemented yet."
        super().__init__(self.message)


class Skill:
    """Base class for skills.
    A skill are a set of plugins that allow the Agent to perform tasks beyond the basic functionality. For example, the Weather skill allows the Agent to fetch the current weather.
    Skills are loaded dynamically from the skills' directory.
    Attributes:
        name -- the name of the skill
        skill_module_path -- the path to the skill module
        skills -- a dictionary of skills
        features -- a dictionary of features"""

    def __call__(self, *args, **kwargs) -> Any:
        return self.call_feature(*args, **kwargs)

    @staticmethod
    def skill_feature(func):
        """Decorator to mark a function as a skill feature.
        This allows the SkillManager to identify the function as a feature of the skill and the Agent to call the function."""
        func.is_skill_feature = True
        return func

    @staticmethod
    def requires_prompt(func):
        """Some functions require the original prompt to be passed as an argument. This decorator marks the function as requiring the prompt.
        NOTE: Adding this decorator means that the agent won't use the param_feature_call method to generate args"""

        func.requires_prompt = True
        return func

    def load_feature(self, feature_name: str) -> Any:
        if hasattr(self, feature_name):
            feature = getattr(self, feature_name)
            if callable(feature):
                return feature
            else:
                raise TypeError(f"Feature {feature_name} is not callable.")
        else:
            raise NotImplementError(feature_name)

    def call_feature(self, feature_name: str, *args, **kwargs) -> Any:
        if hasattr(self, feature_name):
            feature = getattr(self, feature_name)
            if callable(feature):
                feature_args = feature.__code__.co_varnames[:feature.__code__.co_argcount]
                if all(arg in feature_args for arg in kwargs):
                    return feature(*args, **kwargs)
                else:
                    raise TypeError(
                        f"Feature {feature_name} does not accept arguments {kwargs.keys()}. Expected {feature_args}.")
            else:
                raise TypeError(f"Feature {feature_name} is not callable.")
        else:
            raise NotImplementError(feature_name)


class FallBackSkill(Skill):
    """Fallback skill for features that have not been implemented yet.
    Attributes:
        name -- the name of the skill"""

    def __init__(self):
        self.name = "fallback"

    def call_feature(self, *args, **kwargs) -> str:
        return "I'm sorry, I don't know how to do that."


class SkillManager:
    """Class for managing skills.
    Skill Manager is responsible for loading skills and calling features.
    Attributes:
        skill_module_path (str): the path to the skill module
        skills (Dict[str, str]): a dictionary of skills
        features (Dict[str, Any]): a dictionary of features"""

    def __init__(self):
        self.skill_module_path = "alara.skills."
        self.skills: Dict[str, str] = {}
        self.features: Dict[str, Any] = {}
        self.dynamic_load_skill()
        logger.info("Skill Manager initialized.")

    def dynamic_load_skill(self):
        """Load skills dynamically from the skills directory.
        Returns:
            Dict[str, str]: a dictionary of skills"""
        self.skills_dir = Path("alara/skills")
        logger.info(f"Loading skills from {self.skills_dir}")
        self.skill_mapping = {"skills": []}
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_module_path = f"{self.skills_dir.as_posix().replace('/', '.')}.{skill_dir.name}.skill"
                self.skills[skill_dir.name] = skill_module_path
                logger.info(f"Loaded skill {skill_dir.name} from {skill_module_path}")
                try:
                    module = importlib.import_module(skill_module_path)
                    skills = [getattr(module, attr_name) for attr_name in dir(module)
                              if isinstance(getattr(module, attr_name), type) and issubclass(getattr(module, attr_name),
                                                                                             Skill) and getattr(module,
                                                                                                                attr_name) != Skill]
                    for skill in skills:
                        feature_names = [feature_name for feature_name in dir(skill) if
                                         callable(getattr(skill, feature_name)) and hasattr(
                                             getattr(skill, feature_name), "is_skill_feature")]
                        self.features.update({feature_name: skill_dir.name for feature_name in feature_names})
                        self.skill_mapping["skills"].append({"name": skill_dir.name,
                                                             "features": [{"name": feature_name} for feature_name in
                                                                          feature_names]})
                except ImportError as e:
                    logger.warning(f"Failed to import skill {skill_dir.name}: {e}")
                except AttributeError:
                    logger.warning(f"Skill {skill_dir.name} not found in module.")
        logger.info(f"Loaded skills: {self.skills}")
        logger.info(f"Loaded features: {self.features}")
        print(self.skill_mapping)

    def call_feature(self, feature_name: str, *args, **kwargs) -> Any:
        """Call a feature.
        Args:
            feature_name (str): the name of the feature
            *args: positional arguments
            **kwargs: keyword arguments"""
        if feature_name in self.features:
            skill_name = self.features[feature_name]
            skill = self.load_skill(skill_name)
            return skill.call_feature(feature_name, *args, **kwargs)
        else:
            raise NotImplementError(feature_name)

    def load_skill(self, skill_name: str) -> Skill:
        """Load a skill.
        Args:
            skill_name (str): the name of the skill
        Returns:
            Skill: the skill object"""
        if skill_name not in self.skills:
            raise NotImplementError(skill_name)
        skill_module_path = self.skills[skill_name]
        module = importlib.import_module(skill_module_path)
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Skill) and attr != Skill:
                return attr()
        logger.info(f"Skill {skill_name} not found in module {skill_module_path}")
        return FallBackSkill()

if __name__ == "__main__":
    skill_manager = SkillManager()
    skill_manager.call_feature("current_weather")
