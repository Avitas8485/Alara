from hestia.tools.scheduler import SchedulerManager
from hestia.automation.event import Event, EventBus, StateMachine, State

import yaml
"""Sample automation file
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
]"""


class Handler:
    def __init__(self) -> None:
        self.state_machine = StateMachine()
        self.event_bus = EventBus()
        self.state_machine = StateMachine()
        self.load_automations()
    
    def load_automations(self):
        # load automation from file
        # for now, we will just create the automations here
        
        with open('hestia/automation/automations.yaml', 'r') as file:
            self.automations = yaml.load(file, Loader=yaml.FullLoader)
        print(f"Automations: {self.automations}")
        self.trigger = Trigger(self, self.event_bus, self.state_machine)
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
                    
        
    
    
    def get_related_automations(self, trigger_type: str, trigger_data: dict):
        # get automations that have the trigger
        # here, we filter the automations to see which one has the trigger
        # the so filter by trigger type and then trigger data
        filtered_automations = []
        for automation in self.automations:
            for trigger in automation['triggers']:
                print(f"Trigger: {trigger}")
                if trigger['type'] == trigger_type and trigger_data.items() <= trigger.items():
                    print(f"Trigger found: {trigger} with data: {trigger_data}")
                    filtered_automations.append(automation)
                    print(f"Filtered automations: ", [filtered['alias'] for filtered in filtered_automations])
        return filtered_automations
    
    def check_conditions(self, automation: dict):
        # check the conditions of the automation
        # if the conditions are met, return True
        # else, return False
        # since conditions are optional, we will return True if the automation has no conditions
        print(f"Checking conditions for automation: {automation['alias']}")
        '''for condition in automation['conditions']:
            entity_id = condition['entity_id']
            state = condition['state']
            print(f"Checking condition: {condition}")
            current_state = self.state_machine.get_state(entity_id)
            print(f"Current state: {current_state}")
            for key, value in condition.items():
                if key != 'entity_id' and (key not in current_state or current_state[key] != value):
                    print(f"Condition not met: {condition}")
                    return False
        print(f"Conditions met for automation: {automation['alias']}")
        return True'''
           
    def execute_actions(self, automation: dict):
        # execute the actions of the automation
        # the actions are executed by the hub
        for action in automation['actions']:
            # execute the action
            print(f"Executing action: {action}")
            pass
        
    def handle_trigger(self, trigger_type: str, trigger_data: dict):
        automations = self.get_related_automations(trigger_type, trigger_data)
        for automation in automations:
            if self.check_conditions(automation):
                self.execute_actions(automation)
        
        
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
    def __init__(self, handler: Handler, event_bus: EventBus, state_machine: StateMachine) -> None:
        self.handler = handler
        self.event_bus = event_bus
        self.state_machine = state_machine
        
    def fire(self, trigger_type: str, **kwargs):
        """Fire a trigger
        Args:
        trigger_type: str: the type of trigger
        kwargs: dict: the data to pass to the trigger
        """
        print(f"Trigger fired: {trigger_type} with data: {kwargs}")
        self.handler.handle_trigger(trigger_type, kwargs)
                
    def cron_trigger(self,**kwargs):
        """Add a cron trigger
        Args:
        kwargs: dict: the data to pass to the cron trigger"""
        schedule_manager = SchedulerManager()
        schedule_manager.add_job(job_function=lambda: self.fire('cron', **kwargs), trigger='cron', **kwargs)
        
    def interval_trigger(self, **kwargs):
        """Add an interval trigger
        Args:
        kwargs: dict: the data to pass to the interval trigger"""
        schedule_manager = SchedulerManager()
        schedule_manager.add_job(job_function=lambda: self.fire('interval', **kwargs), trigger='interval', **kwargs)
        
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
    handler = Handler()
    light = Lights(handler.state_machine)
    light.turn_on()
    alarm = Alarm(handler.event_bus)
    while True:
        pass
    


