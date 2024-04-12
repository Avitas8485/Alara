import importlib

import json
from hestia.llm.grammar.pydantic_models_to_grammar import create_dynamic_model_from_function
import logging
from typing import Dict
logger = logging.getLogger(__name__)
from typing import Any


class NotImplementError(Exception):
    def __init__(self, feature_name):
        """Raise when a feature has not been implemented yet."""
        self.feature_name = feature_name
        self.message = f"Feature {feature_name} has not been implemented yet."
        super().__init__(self.message)
        

class Skill:
    def __call__(self, *args, **kwargs) -> Any:
        """Call the skill."""
        return self.call_feature(*args, **kwargs)
    
    
    def call_feature(self, feature_name: str, *args, **kwargs) -> Any:
        """Call a feature of the skill."""
        feature = getattr(self, feature_name, None)
        if feature is None:
            raise NotImplementError(feature_name)
        return feature(*args, **kwargs)
    
    
    
class SkillManager:
    def __init__(self) -> None:
        self.skill_module_path = "hestia.skills."
        self.skills: Dict[str, Skill] = {}
        self.skills_map: Dict[str, str] = self._load_skills_map()

    def _load_skills_map(self) -> Dict[str, str]:
        with open("hestia/skills/skills.json") as f:
            return json.load(f)

    def load_skill(self, intent: str) -> None:
        if intent in self.skills:
            return
        try:
            skill_name = self.skills_map.get(intent, intent)
            module = importlib.import_module(f"{self.skill_module_path}{intent}")
            skill_class = getattr(module, skill_name)
            self.skills[intent] = skill_class()
        except ImportError:
            logger.warning(f"Failed to import skill {intent}.")
        except AttributeError:
            logger.warning(f"Skill {intent} not found in module.")

    def add_skill(self, skill: Skill, skill_name: str) -> None:
        self.skills[skill_name] = skill

    def get_skill(self, skill_name: str) -> Skill | None:
        self.load_skill(skill_name)
        return self.skills.get(skill_name)

    def call_skill(self, skill_name: str, *args, **kwargs) -> Any:
        skill = self.get_skill(skill_name)
        if skill is not None:
            return skill(*args, **kwargs)
        else:
            raise NotImplementError(skill_name)

    def create_model(self, skill_name: str, feature_name: str) -> Any:
        skill = self.get_skill(skill_name)
        if skill is not None:
            feature = getattr(skill, feature_name)
            return create_dynamic_model_from_function(feature)
        else:
            raise NotImplementError(skill_name)