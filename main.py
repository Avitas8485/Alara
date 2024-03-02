'''
from hestia.agent import Agent

agent = Agent()
agent.run()
'''

from hestia.routines.morning.morning_routine import morning_preparation, morning_presentation

morning_preparation()
morning_presentation()