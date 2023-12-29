from flask import Flask, render_template
from hestia.tools.system_and_utility.scheduler import SchedulerManager

from hestia.routines.morning.morning_routine import schedule_morning_routine
app = Flask(__name__)

scheduler = SchedulerManager()
schedule_morning_routine()


@app.route("/")
def home():
    return render_template("index.html")







if __name__ == "__main__":
    app.run(debug=True)
    
    