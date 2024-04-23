from alara.skills.skill_manager import SkillManager
from alara.automation.condition import Condition
from alara.automation.action import Action
from alara.tools.scheduler import SchedulerManager
from alara.automation.event import Event, EventBus, StateMachine, State
from alara.lib.logger import logger
from alara.llm.llama_chat_completion import LlamaChatCompletion
from typing import List
import os
import yaml


class AutomationHandler:
    """A class that is responsible for handling the automation workflow
    The handler is responsible for:
    - loading automations from a file
    - handling triggers
    - checking conditions
    - executing actions
    - interacting with the state machine
    - interacting with the event bus
    Attributes:
    state_machine: StateMachine: the state machine to manage states of entities
    event_bus: EventBus: the event bus to emit and listen for events
    condition: Condition: functions as a condition checker
    automations: List[dict]: a list of automations
    """

    def __init__(self) -> None:
        self.trigger = None
        self.automations = None
        self.state_machine = StateMachine()
        self.event_bus = EventBus()
        self.state_machine = StateMachine()
        self.condition = Condition(self.state_machine)
        self.skill_manager = SkillManager()
        self.llm = LlamaChatCompletion()
        self.scheduler = SchedulerManager()
        self.action = Action(self.event_bus, self.state_machine, self.condition, self.skill_manager)
        self.load_automations()

    def load_automations(self):
        """Load automations from a file"""
        file_path = os.path.join('alara', 'automation', 'automations.yaml')
        with open(file_path, 'r') as file:
            self.automations = yaml.safe_load(file)
        logger.debug(f"Loaded automations: {self.automations}")
        self.trigger = Trigger(self, self.event_bus, self.state_machine)
        if not self.automations:
            logger.warning("No automations found")
            return
        for automation in self.automations:
            for trigger in automation['triggers']:
                trigger_args = {key: value for key, value in trigger.items() if key != 'type'}
                trigger_type = trigger['type']
                if trigger_type == 'interval':
                    self.trigger.interval_trigger(**trigger_args)
                elif trigger_type == 'event':
                    self.trigger.event_trigger(**trigger_args)
                elif trigger_type == 'state':
                    self.trigger.state_trigger(**trigger_args)
                elif trigger_type == 'cron':
                    self.trigger.cron_trigger(**trigger_args)

    def get_related_automations(self, trigger_type: str, trigger_data: dict) -> list[dict]:
        """Get automations related to the trigger
        Args:
        trigger_type: str: the type of trigger
        trigger_data: dict: the data of the trigger
        Returns:
        List[dict]: a list of automations related to the trigger"""
        filtered_automations = []
        if self.automations is None:
            return filtered_automations
        for automation in self.automations:
            for trigger in automation['triggers']:
                if trigger['type'] == trigger_type and all(
                        trigger_data.get(key) == value for key, value in trigger_data.items() if key != 'type'):
                    logger.debug(f"Found related automation: {automation['alias']}")
                    filtered_automations.append(automation)
                    logger.debug(f"Filtered automations: ", [filtered['alias'] for filtered in filtered_automations])
        return filtered_automations

    def check_conditions(self, automation: dict) -> bool:
        """Check the conditions of the automation
        Args:
        automation: dict: the automation to check conditions for
        Returns:
        bool: True if all conditions are met, else False"""
        logger.info(f"Checking conditions for automation: {automation['alias']}")
        conditions = automation.get('conditions')
        if not conditions or len(conditions) == 0:
            logger.debug(f"No conditions found for automation: {automation['alias']}")
            return True
        return self.condition.check_condition(automation['conditions'])

    def execute_actions(self, automation: List[dict]):
        """A placeholder for executing the actions of the automation
            Args:
            automation: dict: the automation to execute actions for"""
        logger.info(f"Executing actions for automation: {automation}")
        if not automation or len(automation) == 0:
            logger.info(f"No actions found for automation: {automation}")
            return
        return self.action.choose_action(automation)

    def handle_trigger(self, trigger_type: str, trigger_data: dict):
        """Handle a trigger
        Args:
        trigger_type: str: the type of trigger
        trigger_data: dict: the data of the trigger"""
        automations = self.get_related_automations(trigger_type, trigger_data)
        for automation in automations:
            if self.check_conditions(automation):
                self.execute_actions(automation['actions'])


class Trigger:
    """A class to handle triggers
    A trigger is anything that can cause an automation to run
    Triggers can be of different types, such as:
    - interval: a trigger that runs at a regular interval
    - cron: a trigger that runs at a specific time
    - event: a trigger that runs when an event occurs
    - state: a trigger that runs when the state of an entity changes
    Args:
    handler: Handler: the handler to handle the trigger
    event_bus: EventBus: the event bus to emit events
    state_machine: StateMachine: the state machine to change states
    """

    def __init__(self, handler: AutomationHandler, event_bus: EventBus, state_machine: StateMachine) -> None:
        self.handler = handler
        self.event_bus = event_bus
        self.state_machine = state_machine

    def fire(self, trigger_type: str, **kwargs):
        """Fire a trigger
        Args:
        trigger_type: str: the type of trigger
        kwargs: dict: relevant data for the trigger
        """
        logger.debug(f"Trigger fired: {trigger_type} with data: {kwargs}")
        self.handler.handle_trigger(trigger_type, kwargs)

    def cron_trigger(self, **kwargs):
        """Add a cron trigger
        Args:
        kwargs: dict: the data to pass to the cron trigger"""
        handler.scheduler.add_job(job_function=lambda: self.fire('cron', **kwargs), trigger='cron', **kwargs)

    def interval_trigger(self, **kwargs):
        """Add an interval trigger
        Args:
        kwargs: dict: the data to pass to the interval trigger"""
        handler.scheduler.add_job(job_function=lambda: self.fire('interval', **kwargs), trigger='interval', **kwargs)
        
        
    def event_trigger(self, event_name: str, **kwargs):
        """Add an event trigger
        Args:
        event_name: str: the name of the event to listen for"""
        self.event_bus.add_listener(event_name, lambda event: self.fire(event_name, **kwargs))

    def state_trigger(self, entity_id: str, **kwargs):
        """Add a state trigger
        Args:
        entity_id: str: the id of the entity to listen for"""
        self.state_machine.listen_state(entity_id, lambda state: self.fire(entity_id, **kwargs))


# NOTE: The following classes are not used in the codebase. They are for experimentation purposes only. ###

class Integration:
    """A class to handle integrations
    An integration is a class that interacts with the hub
    Integrations can be of different types, such as:
    - lights: an integration that controls lights
    - alarm: an integration that controls alarms
    Args:
    state_machine: StateMachine: the state machine to change states
    event_bus: EventBus: the event bus to emit events
    """

    def __init__(self, state_machine: StateMachine, event_bus: EventBus) -> None:
        self.devices = {}
        self.state_machine = state_machine
        self.event_bus = event_bus

    def add_device(self, device: dict):
        """Add a device to the integration
        Args:
        device: dict: the device to add to the integration
        """
        self.devices[device['entity_id']] = device
        self.state_machine.add_state(State(device['entity_id'], device['state']))

    def remove_device(self, entity_id: str):
        """Remove a device from the integration
        Args:
        entity_id: str: the id of the device to remove from the integration"""
        if entity_id in self.devices:
            del self.devices[entity_id]
            self.state_machine.remove_state(entity_id)

    def listen_state(self, entity_id: str, callback):
        """Add a listener to a device's state
        Args:
        entity_id: str: the id of the device
        callback: Callable[..., None]: the function to call when the device's state changes"""
        self.state_machine.listen_state(entity_id, callback)

    def listen_event(self, event_type: str, callback):
        self.event_bus.add_listener(event_type, callback)


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
    handler = AutomationHandler()
    light = Lights(handler.state_machine)
    alarm = Alarm(handler.event_bus)
    while True:
        pass
