from alara.automation.automation_handler import AutomationHandler
from alara.automation.event import Event, State


class Entity:
    def __init__(self, automation_handler: AutomationHandler):
        self.entity_id: str = ''
        self.handler: AutomationHandler = automation_handler
        self.entity_description = None
        self.state = "unknown"
        self.attributes = {}

    def add_entity_state(self):
        self.handler.state_machine.add_state(
            State(entity_id=self.entity_id, state=self.state, attributes=self.attributes))
        self.handler.event_bus.emit_event(Event("entity_added", {"entity_id": self.entity_id}))

    def update_entity_state(self, new_state: str, attributes: dict):
        self.handler.state_machine.set_state(entity_id=self.entity_id, new_state=new_state, attributes=attributes)
        self.state = new_state
        self.attributes = attributes
        self.handler.event_bus.emit_event(Event("entity_updated", {"entity_id": self.entity_id}))

    def remove_entity_state(self):
        self.handler.state_machine.remove_state(entity_id=self.entity_id)
        self.handler.event_bus.emit_event(Event("entity_removed", {"entity_id": self.entity_id}))

# NOTE: The following classes are not used in the codebase. They are provided as examples of how to create entities. ###

class Lights(Entity):
    def __init__(self, automation_handler: AutomationHandler):
        super().__init__(automation_handler)
        self.entity_id = "lights"
        self.entity_description = "A set of lights in a room."
        self.state = "off"
        self.attributes = {"brightness": 0}
        self.handler = automation_handler
        self.add_entity_state()

    def turn_on(self):
        self.update_entity_state("on", {"brightness": 100})
        self.handler.event_bus.emit_event(Event("lights_on", {"entity_id": self.entity_id, "brightness": 100}))

    def turn_off(self):
        self.update_entity_state("off", {"brightness": 0})
        self.handler.event_bus.emit_event(Event("lights_off", {"entity_id": self.entity_id, "brightness": 0}))

    def set_brightness(self, brightness):
        self.update_entity_state("on", {"brightness": brightness})
        self.handler.event_bus.emit_event(
            Event("lights_brightness_changed", {"entity_id": self.entity_id, "brightness": brightness}))

    def remove(self):
        self.remove_entity_state()


class Thermostat(Entity):
    def __init__(self, automation_handler: AutomationHandler):
        super().__init__(automation_handler)
        self.entity_id = "thermostat"
        self.entity_description = "A thermostat in a room."
        self.state = "off"
        self.attributes = {"temperature": 0}
        self.handler = automation_handler
        self.add_entity_state()

    def turn_on(self, temperature):
        self.update_entity_state("on", {"temperature": temperature})
        self.handler.event_bus.emit_event(
            Event("thermostat_on", {"entity_id": self.entity_id, "temperature": temperature}))

    def turn_off(self):
        self.update_entity_state("off", {"temperature": 0})
        self.handler.event_bus.emit_event(Event("thermostat_off", {"entity_id": self.entity_id, "temperature": 0}))

    def set_temperature(self, temperature):
        self.update_entity_state("on", {"temperature": temperature})
        self.handler.event_bus.emit_event(
            Event("thermostat_temperature_changed", {"entity_id": self.entity_id, "temperature": temperature}))

    def remove(self):
        self.remove_entity_state()
