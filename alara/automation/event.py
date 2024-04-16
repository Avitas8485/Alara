from alara.lib.logger import logger
from typing import Dict, Any, Callable, Optional
from enum import Enum
from datetime import datetime


class EventOrigin(Enum):
    """Enum for event origin
    values:
    LOCAL: event was triggered locally
    REMOTE: event was triggered remotely"""
    LOCAL = "LOCAL"
    REMOTE = "REMOTE"


class Event:
    """Class to represent an event
    Attributes:
    event_type: str: the type of event e.g. light_turned_on
    data: dict: the data associated with the event
    origin: EventOrigin: the origin of the event
    time_fired: datetime: the time the event was fired"""

    def __init__(self,
                 event_type: str,
                 data: Optional[Dict[str, Any]] = None,
                 origin: EventOrigin = EventOrigin.LOCAL,
                 time_fired: Optional[datetime] = None) -> None:
        self.event_type = event_type
        self.data = data if data else {}
        self.origin = origin
        self.time_fired = time_fired if time_fired else datetime.now()

    def as_dict(self) -> Dict[str, Any]:
        """Return the event as a dictionary"""
        return {
            "event_type": self.event_type,
            "data": self.data,
            "origin": self.origin,
            "time_fired": self.time_fired
        }


class EventBus:
    """Class to represent an event bus
    An event bus is a mechanism for publishing and subscribing to events\n
    Attributes:
    listeners: dict: a dictionary of event types and their listeners
    A listener does exactly what it sounds like: it listens for events and responds to them.
    """

    def __init__(self) -> None:
        self.listeners: dict[str, list[Callable[..., None]]] = {}

    def add_listener(self, event_type: str, callback: Callable[..., None]):
        """Add a listener to an event type
        Args:
        event_type: str: the type of event to listen to
        callback: Callable[..., None]: the function to call when the event is triggered"""
        if not isinstance(event_type, str):
            raise TypeError('event_type must be a string')
        if not callable(callback):
            raise TypeError('callback must be a callable function')
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def remove_listener(self, event_type: str, callback: Callable[..., None]):
        """Remove a listener from an event type
        Args:
        event_type: str: the type of event to remove the listener from
        callback: Callable[..., None]: the function to remove from the event type's listeners"""
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)

    def emit_event(self, event: Event):
        event_type = event.event_type
        if event_type in self.listeners:
            for listener in self.listeners[event_type]:
                listener(event)
        else:
            logger.warning(f'Warning: No listeners for event type {event_type}')


class State:
    """
    A state is a particular setting or condition of an entity at a particular time
    Attributes:
    entity_id: str: the id of the entity
    state: str: the state of the entity
    attributes: dict: the attributes of the entity
    last_changed: datetime: the time the state was last changed
    last_updated: datetime: the time the state was last updated
    context: dict: the context of the state
    """

    def __init__(self, entity_id: str, state: str, attributes: Optional[Dict[str, Any]] = None,
                 last_changed: Optional[datetime] = None, last_updated: Optional[datetime] = None,
                 context: Optional[Dict[str, Any]] = None) -> None:
        self.entity_id = entity_id
        self.state = state
        self.attributes = attributes if attributes else {}
        self.last_changed = last_changed if last_changed else datetime.now()
        self.last_updated = last_updated if last_updated else datetime.now()
        self.context = context if context else {}

    def __repr__(self) -> str:
        return (f"State(entity_id={self.entity_id}, state={self.state}, attributes={self.attributes}, "
                f"last_changed={self.last_changed}, last_updated={self.last_updated}, context={self.context})")

    @staticmethod
    def from_dict(state_dict: dict[str, Any]) -> 'State':
        """Convert a dictionary to a State
        Args:
        state_dict: dict: a dictionary representation of a state
        Returns:
        State: the state object"""
        return State(
            state_dict['entity_id'],
            state_dict['state'],
            state_dict['attributes'],
            state_dict['last_changed'],
            state_dict['last_updated'],
            state_dict['context']
        )

    def as_dict(self) -> dict[str, Any]:
        """Return the state as a dictionary"""
        return {
            "entity_id": self.entity_id,
            "state": self.state,
            "attributes": self.attributes,
            "last_changed": self.last_changed,
            "last_updated": self.last_updated,
            "context": self.context
        }


class StateMachine:
    """Class to represent a state machine
    A state machine is a mechanism for managing the states of entities
    Attributes:
    states: dict: a dictionary of entity ids and their states
    event_bus: EventBus: an instance of the EventBus class"""

    def __init__(self):
        self.states: Dict[str, State] = {}
        self.event_bus = EventBus()

    @staticmethod
    def to_state(state_dict: dict[str, Any]) -> State:
        """Convert a dictionary to a State
        Args:
        state_dict: dict: a dictionary representation of a state
        Returns:
        State: the state object"""
        return State(
            state_dict['entity_id'],
            state_dict['state'],
            state_dict['attributes'],
            state_dict['last_changed'],
            state_dict['last_updated'],
            state_dict['context']
        )

    @staticmethod
    def from_state(state: State) -> dict[str, Any]:
        """Convert a State to a dictionary
        Args:
        state: State: the state to convert to a dictionary
        Returns:
        dict: a dictionary representation of the state"""
        return {
            "entity_id": state.entity_id,
            "state": state.state,
            "attributes": state.attributes,
            "last_changed": state.last_changed,
            "last_updated": state.last_updated,
            "context": state.context
        }

    def add_state(self, state: State):
        """Add a state to the state machine
        Args:
        state: State: the state to add to the state machine
        """
        self.states[state.entity_id] = state

    def remove_state(self, entity_id: str):
        """Remove a state from the state machine
        Args:
        entity_id: str: the id of the entity to remove from the state machine"""
        if entity_id in self.states:
            del self.states[entity_id]

    def get_state(self, entity_id: str) -> State:
        """Get the state of an entity
        Args:
        entity_id: str: the id of the entity
        Returns:
        State: the state of the entity"""
        if entity_id not in self.states:
            raise ValueError(f'Entity {entity_id} not found in state machine')
        return self.states[entity_id]

    def set_state(self, entity_id: str, new_state: State | str, attributes: Optional[dict[str, Any]] = None):
        """Set the state of an entity
        Args:
        entity_id: str: the id of the entity
        state: State: the state to set for the entity"""
        # get the current state of the entity
        current_state = self.get_state(entity_id)
        if isinstance(new_state, str):
            new_state = State(
                entity_id=entity_id,
                state=new_state,
                attributes=attributes if attributes else current_state.attributes,
                last_changed=datetime.now(),
                last_updated=datetime.now(),
                context=current_state.context
            )
        updated_state = State(
            entity_id=entity_id,
            state=new_state.state,
            attributes=attributes if attributes else current_state.attributes,
            last_changed=datetime.now(),
            last_updated=datetime.now(),
            context=current_state.context
        )
        self.states[entity_id] = updated_state

    def listen_state(self, entity_id: str, callback: Callable[..., None]):
        """Add a listener to an entity's state
        Args:
        entity_id: str: the id of the entity
        callback: Callable[..., None]: the function to call when the entity's state changes"""

        def state_change_listener(event: Event):
            """A listener to listen for state changes"""
            if event.data['entity_id'] == entity_id:
                callback(event)

        self.event_bus.add_listener('state_changed', state_change_listener)

    def fire_event(self, event: Event):
        """Fire an event
        Args:
        event: Event: the event to fire"""
        if self.event_bus:
            self.event_bus.emit_event(event)
        else:
            print('Warning: No event bus to fire event')

    def listen_event(self, event_type: str, callback: Callable[..., None]):
        """Add a listener to an event type
        Args:
        event_type: str: the type of event to listen to
        callback: Callable[..., None]: the function to call when the event is triggered"""
        self.event_bus.add_listener(event_type, callback)


class Lights:
    """A class to handle lights
    Args:
    state_machine: StateMachine: the state machine to change states
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """

        @type state_machine: StateMachine
        """
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
        """

        @type event_bus: EventBus
        """
        self.event_bus = event_bus

    def trigger_alarm(self):
        """Trigger the alarm"""
        self.event_bus.emit_event(Event("alarm_triggered", {"data": "some data"}))

    def stop_alarm(self):
        """Stop the alarm"""
        self.event_bus.emit_event(Event("alarm_stopped", {"data": "some data"}))


if __name__ == '__main__':
    state_machine = StateMachine()
    event_bus = EventBus()
    lights = Lights(state_machine)
    alarm = Alarm(event_bus)
