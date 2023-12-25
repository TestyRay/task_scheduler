import schedule
import time
from datetime import datetime
from threading import Thread

class TaskScheduler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.scheduler = schedule.Scheduler()
            cls._instance.thread = Thread(target=cls._instance.run_continuously)
            cls._instance.thread.daemon = True
            cls._instance.thread.start()
        return cls._instance

    def run_continuously(self):
        while True:
            self.scheduler.run_pending()
            time.sleep(1)

    def schedule_task(self, task_id, date_time, func, *args, **kwargs):
        delay = (date_time - datetime.now()).total_seconds()
        if delay > 0:
            def job_that_deletes_itself():
                func(*args, **kwargs)
                return schedule.CancelJob
            self.scheduler.every(delay).seconds.do(job_that_deletes_itself).tag(task_id)

    def clear_scheduled_task(self, task_id):
        self.scheduler.clear(task_id)