from .event import StateMachine
from datetime import datetime
from .event import Event, EventBus, State
from alara.lib.logger import logger
from typing import List


class Condition:
    """Condition class to check the condition specified in the automation
    Args:
        state_machine (StateMachine): Instance of StateMachine class
        """

    def __init__(self, state_machine: StateMachine) -> None:
        """

        @type state_machine: StateMachine
        """
        self.state_machine = state_machine

    def check_state(self, entity_id: str, required_state: dict) -> bool:
        """Check the state of the entity
        Args:
            entity_id (str): Entity ID
            required_state (dict): Required state of the entity
        Returns:
            bool: True if the current state of the entity is same as the required state, else False"""
        value = self.state_machine.get_state(entity_id)
        value = value.as_dict()
        if value['state'] == required_state:
            return True
        return False

    def check_time(self, start_time: str | datetime, end_time: str | datetime) -> bool:
        """Check if the current time is within the specified time range
        Args:
            start_time (datetime): Start time
            end_time (datetime): End time"""
        if not isinstance(start_time, datetime):
            start_time = datetime.strptime(start_time, '%H:%M:%S')
        if not isinstance(end_time, datetime):
            end_time = datetime.strptime(end_time, '%H:%M:%S')
        now = datetime.now()
        if start_time and now < start_time:
            return False
        if end_time and now > end_time:
            return False
        return True

    def check_condition(self, conditions: List[dict]) -> bool:
        """Check the conditions specified in the automation.
        Args:
            conditions: List of conditions.
            Returns:
            bool: True if all the conditions are met, else False."""
        for cond in conditions:
            condition_type = cond.get('condition')
            if condition_type == 'state':
                entity_id = cond.get('entity_id')
                required_state = cond.get('state')
                if entity_id and required_state:
                    if not self.check_state(entity_id, required_state):
                        return False
            elif condition_type == 'time':
                start_time = cond.get('start_time')
                end_time = cond.get('end_time')
                if start_time and end_time:
                    if not self.check_time(start_time, end_time):
                        return False
            else:
                logger.error(f"Warning: Invalid condition type '{condition_type}'")
        return True

# NOTE: The following classes are not used in the codebase. They are for experimentation purposes only. ###
class Lights:
    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine
        self.state_machine.add_state(State("light", "off"))

    def turn_on(self, data=None):
        if data is None:
            data = {"data": "some data"}
        print("Turning on the light")
        self.state_machine.set_state("light", State("light", "on"))
        self.state_machine.fire_event(Event("light_turned_on", data))

    def turn_off(self, data=None):
        if data is None:
            data = {"data": "some data"}
        print("Turning off the light")
        self.state_machine.set_state("light", State("light", "off"))
        self.state_machine.fire_event(Event("light_turned_off", data))


class Alarm:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def trigger_alarm(self, data=None):
        if data is None:
            data = {"data": "some data"}
        self.event_bus.emit_event(Event("alarm_triggered", data))

    def stop_alarm(self, data=None):
        if data is None:
            data = {"data": "some data"}
        self.event_bus.emit_event(Event("alarm_stopped", data))


if __name__ == "__main__":
    state_machine = StateMachine()
    event_bus = EventBus()
    condition = Condition(state_machine)
    light = Lights(state_machine)
    print(condition.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'off'}]))
    print(condition.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'on'}]))
    light.turn_on()
    print(condition.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'on'}]))
    print(condition.check_condition([{'condition': 'state', 'entity_id': 'light', 'state': 'off'}]))
    print(condition.check_condition([{'condition': 'time', 'start_time': '22:00:00', 'end_time': '23:00:00'}]))
    print(condition.check_condition([{'condition': 'time', 'start_time': '22:00:00', 'end_time': '23:00:00'}]))
