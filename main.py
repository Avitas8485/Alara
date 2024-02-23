#from flask import Flask, render_template
#from hestia.tools.system_and_utility.scheduler import SchedulerManager
#from hestia.lib.hestia_logger import logger
#from hestia.routines.morning.morning_routine import morning_preparation, morning_presentation

from kivy.app import App
from kivy.uix.label import Label
from datetime import datetime
import time
from kivy.clock import Clock


class Hestia(App):
    
    def build(self):
        self.label = Label(text="00:00:00")
        Clock.schedule_interval(self.update, 1)
        return self.label
    
    def update(self, *args):
        #self.label.text = time.strftime("%H:%M:%S")
        self.label.text = datetime.now().strftime("%d %b %Y %H:%M:%S")
        
    def on_stop(self):
        print("on_stop")
        return True
    
    def on_pause(self):
        print("on_pause")
        return True
    
    def on_resume(self):
        print("on_resume")
        return True
    
    def on_start(self):
        print("on_start")
        return True
    
    
    
        
if __name__ == "__main__":
    Hestia().run()
    
    '''
app = Flask(__name__)

scheduler = SchedulerManager()
scheduler.start_scheduler()
def schedule_morning_routine():
    """Schedule the morning routine."""
    logger.info("Scheduling morning routine...")
    scheduler.add_job(morning_preparation,trigger="cron",hour=7,minute=00)
    scheduler.add_job(morning_presentation,trigger="cron",hour=8,minute=30)
    logger.info("Morning routine scheduled.")






@app.route("/")
def home():
    return render_template("index.html")







if __name__ == "__main__":
    app.run(debug=False)
    
    '''