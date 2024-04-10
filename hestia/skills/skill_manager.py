import importlib
from hestia.skills.base_skill import NotImplementError, Skill
import json
from hestia.llm.grammar.pydantic_models_to_grammar import create_dynamic_model_from_function

class SkillManager:
    def __init__(self) -> None:
        self.skill_module_path = "hestia.skills."
        self.skills = {}
        with open("hestia/skills/skills.json") as f:
            self.skills_map: dict = json.load(f)
        for skill in self.skills_map:
            self.load_skill(skill)
        
    def load_skill(self, intent):
        try:
            skill_name = self.skills_map.get(intent, intent)
            module = importlib.import_module(f"{self.skill_module_path}{intent}")
            skill_class = getattr(module, skill_name)
            self.skills[intent] = skill_class
        except (ImportError, AttributeError) as e:
            print(f"Skill {intent} not found {e}")
            
    def add_skill(self, skill: Skill, skill_name: str):
        self.skills[skill_name] = skill
        
    def get_skill(self, skill_name):
        return self.skills.get(skill_name)

    def call_skill(self, skill_name, *args, **kwargs):
        skill = self.skills.get(skill_name)
        if skill is None:
            self.load_skill(skill_name)
            skill = self.skills.get(skill_name)
        if skill is not None:
            return skill(*args, **kwargs)
        else:
            raise NotImplementError(skill_name)
        
    def create_model(self, skill_name, feature_name):
        skill = self.skills.get(skill_name)
        if skill is None:
            self.load_skill(skill_name)
            skill = self.skills.get(skill_name)
        if skill is not None:
            feature = getattr(skill, feature_name)
            return create_dynamic_model_from_function(feature)
        else:
            raise NotImplementError(skill_name)
        
            
            

