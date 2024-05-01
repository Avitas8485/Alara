from typing import List
from alara.automation.event import Event, EventBus, StateMachine, State
from alara.automation.condition import Condition
from alara.skills.skill_manager import SkillManager
from alara.lib.logger import logger


class Action:
    """A class to represent an Action that the AI assistant can take.
    Attributes:
        event_bus: EventBus: The event bus to emit events.
        state_machine: StateMachine: The state machine to change states.
        condition: Condition: The condition to check before taking an action.
        skill_manager: SkillManager: The skill manager to call skills.
    """

    def __init__(self, event_bus: EventBus, state_machine: StateMachine, condition: Condition,
                 skill_manager: SkillManager) -> None:
        self.event_bus = event_bus
        self.state_machine = state_machine
        self.condition = condition
        self.skill_manager = skill_manager
        logger.info("Action initialized.")

    def change_state(self, entity_id: str, state: State):
        """Change the state of an entity.
        Args:
            entity_id: (str) The id of the entity (e.g. light, alarm, etc.
            state: (State) The state to change to."""
        if self.state_machine:
            obj = self.state_machine.get_state(entity_id)
            if obj is None:
                self.state_machine.add_state(state)
            else:
                self.state_machine.set_state(entity_id, state)
        else:
            logger.error("State machine is not initialized.")

    def check_condition(self, conditions: List[dict]) -> bool:
        """Check the conditions specified in the automation.
        Args:
            conditions: List[dict]: List of conditions to check.
        Returns:
            bool: True if all the conditions are met, else False."""
        return self.condition.check_condition(conditions)

    def call_skill(self, skill_name: str, *args, **kwargs):
        """Call a skill.
        Args:
            skill_name: str: The name of the skill to call.
            args: The arguments to pass to the skill.
            kwargs: The keyword arguments to pass to the skill."""
        return self.skill_manager.call_feature(skill_name, *args, **kwargs)

    def choose_action(self, actions: List[dict]):
        """Take the action specified in the automation.
        Args:
            actions: List[dict]: List of actions to take."""
        print(f"Taking actions: {actions}")
        for action in actions:
            action_type = action.get('action')
            if action_type == 'change_state':
                entity_id = action.get('entity_id')
                state = action.get('state')
                if entity_id and state:
                    self.change_state(entity_id, state)
            elif action_type == 'call_skill':
                skill_name = action.get('skill_name')
                feature_name = action.get('feature_name')
                if skill_name and feature_name:
                    self.call_skill(feature_name)
            elif action_type == 'check_condition':
                conditions = action.get('conditions')
                if conditions:
                    self.check_condition(conditions)
            else:
                logger.error(f"Invalid action type: {action_type}")


# NOTE: The following classes are not used in the codebase. They are for experimentation purposes only. ###

class Lights:
    """A class to handle lights
    Args:
    state_machine: StateMachine: the state machine to change states
    """

    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine
        self.state_machine.add_state(State("light", "off"))

    def turn_on(self):
        """Turn on the light"""
        self.state_machine.set_state("light", State("light", "on"))
        self.state_machine.fire_event(Event("light_turned_on", {"data": "some data"}))

    def turn_off(self):
        """Turn off the light"""
        self.state_machine.set_state("light", State("light", "off"))
        self.state_machine.fire_event(Event("light_turned_off", {"data": "some data"}))


class Alarm:
    """A class to handle alarms
    Args:
    event_bus: EventBus: the event bus to emit events"""

    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def trigger_alarm(self):
        """Trigger the alarm"""
        self.event_bus.emit_event(Event("alarm_triggered", {"data": "some data"}))

    def stop_alarm(self):
        """Stop the alarm"""
        self.event_bus.emit_event(Event("alarm_stopped", {"data": "some data"}))


if __name__ == "__main__":
    
    event_bus = EventBus()
    state_machine = StateMachine(event_bus)
    condition = Condition(state_machine)
    skill_manager = SkillManager()
    action = Action(event_bus, state_machine, condition, skill_manager)
    lights = Lights(state_machine)
    alarm = Alarm(event_bus)
    action.change_state("light", State("light", "on"))
    print(action.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'off'}]))
    print(action.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'on'}]))
    lights.turn_on()
    print(action.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'on'}]))
    print(action.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'off'}]))
    print(action.call_skill("weather", "get_weather"))
    alarm.trigger_alarm()
