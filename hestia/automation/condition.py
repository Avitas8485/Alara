from event import StateMachine
from datetime import datetime
from event import Event, EventBus, State
from typing import List

"""Condition module for automation
the plan is to check condition based on the condition type specified in the automation
Code is written to be extendable, so that new condition types can be added easily
Sample automation file
[
    {
        'alias': 'Change light state every 30 seconds', 
        'triggers': [
            {'type': 'interval', 'hours': 0, 'minutes': 0, 'seconds': 30}
            ],
        'conditions': [
            {'condition': 'state', 'entity_id': 'light', 'state': 'off'}
            ], 
        'actions': [
            {'service': 'light.turn_on', 'entity_id': 'light'}
            ]
    }, 
    {
        'alias': 'Turn off light after 5 minutes', 
        'triggers': [
            {'type': 'state', 'entity_id': 'light', 'from': 'on', 'to': 'off', 'for': '00:05:00'}
            ], 
        'conditions': [], 
        'actions': [
                {'service': 'light.turn_off', 'entity_id': 'light'}
                ]
    }, 
    {
        'alias': 'Turn off the light at 10:00 PM', 
        'triggers': [
            {'type': 'cron', 'hour': 22, 'minute': 0}
            ], 
        'conditions': [], 
        'actions': [
            {'service': 'light.turn_off', 'entity_id': 'light'}
            ]
        }
]
"""

#something like homeassistant/automation/condition.py
class Condition:
    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine
    
    def check_state(self, entity_id, required_state: dict):
        # check if the state of the entity is as required
        # if for_period is specified, check if the state was as required for the given period
        value = self.state_machine.get_state(entity_id)
        if value['state'] == required_state:
            return True
        return False
    
    def check_time(self, start_time, end_time):
        # check if the current time is within the given range
        now = datetime.now()
        if start_time and now < start_time:
            return False
        if end_time and now > end_time:
            return False
        return True
    
    def check_condition(self, condition: List[dict]):
        # check the condition
        # if the condition is met, return True
        # else, return False
        for cond in condition:
            if cond['condition'] == 'state':
                if not self.check_state(cond['entity_id'], cond['state']):
                    return False
            elif cond['condition'] == 'time':
                if not self.check_time(cond['start_time'], cond['end_time']):
                    return False
        return True
        


class Lights:
    def __init__(self, state_machine: StateMachine) -> None:
        self.state_machine = state_machine
        self.state_machine.add_state(State("light", "off"))

    def turn_on(self, data: dict={"data": "some data"}):
        print("Turning on the light")
        self.state_machine.set_state("light", State("light", "on"))
        self.state_machine.fire_event(Event("light_turned_on", data))

    def turn_off(self, data: dict={"data": "some data"}):
        print("Turning off the light")
        self.state_machine.set_state("light", State("light", "off"))
        self.state_machine.fire_event(Event("light_turned_off", data))


class Alarm:
    def __init__(self, event_bus: EventBus) -> None:
        self.event_bus = event_bus

    def trigger_alarm(self, data: dict={"data": "some data"}):
        self.event_bus.emit_event(Event("alarm_triggered", data))

    def stop_alarm(self, data: dict={"data": "some data"}):
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
    
    
    
    
    