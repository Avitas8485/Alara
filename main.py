'''
from hestia.agent import Agent

agent = Agent()
agent.run()
'''

from hestia.tools.scheduler import SchedulerManager

scheduler = SchedulerManager()
def test():
    print('test')
#scheduler.add_job(job_function=test, job_id='test', trigger='interval', seconds=2)
scheduler.get_jobs()
scheduler.modify_job(job_id='test', job_function=test, trigger='interval', seconds=5)
