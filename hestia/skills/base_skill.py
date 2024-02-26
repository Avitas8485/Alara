from typing import Any


class NotImplementError(Exception):
    def __init__(self, feature_name):
        """Raise when a feature has not been implemented yet."""
        self.feature_name = feature_name
        self.message = f"Feature {feature_name} has not been implemented yet."
        super().__init__(self.message)
        

class BaseSkill:
    def call_feature(self, feature_name: str, *args, **kwargs) -> Any:
        """Call a feature of the skill."""
        feature = getattr(self, feature_name, None)
        if feature is None:
            raise NotImplementError(feature_name)
        return feature(*args, **kwargs)
    
    
    

    
    
    