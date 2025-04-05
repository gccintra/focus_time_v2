from datetime import date, timedelta
from app.models.todo import ToDo
from app.models.exceptions import TaskValidationError
from app.models.base_model import BaseModel

class Task(BaseModel):    
    TASK_TITLE_MAX_LEN = 30

    def __init__(self, user_FK, identificator, title, color, seconds_in_focus_per_day=None, status=None): 
        self.__user_FK = user_FK
        self.__identificator = identificator

        self._title = None
        self.title = title 

        self._color = color
        self._seconds_in_focus_per_day = seconds_in_focus_per_day or {}
        self._status = status or 'active'
         
    @property
    def user_FK(self):
        return self.__user_FK

    @property
    def identificator(self):
        return self.__identificator

    @property
    def color(self):
        return self._color

    @property
    def status(self):
        return self._status

    @property
    def seconds_in_focus_per_day(self):
        return self._seconds_in_focus_per_day

    @property
    def today_total_seconds(self):
        today = str(date.today())  
        return int(self._seconds_in_focus_per_day.get(today, 0))

    @property
    def today_total_minutes(self):
        return round(self.today_total_seconds / 60, 1)
    
    @property
    def today_total_time(self):
        hours, remainder = divmod(self.today_total_seconds, 3600)
        minutes = round(remainder / 60)
        return f"{hours:02}h{minutes:02}m"
    
    @property
    def today_total_time_timer(self):
        hours, remainder = divmod(self.today_total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    @property
    def week_total_seconds(self):
        today = date.today()
        last_7_days = [(today - timedelta(days=i)).isoformat() for i in range(7)]
        return sum(int(self._seconds_in_focus_per_day.get(day, 0)) for day in last_7_days)

    @property
    def week_total_minutes(self):
        return round(self.week_total_seconds / 60.0)

    @property
    def week_total_time(self):
        hours, remainder = divmod(self.week_total_seconds, 3600)
        minutes = round(remainder / 60)
        return f"{hours:02}h{minutes:02}m"
    
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value:
            raise TaskValidationError(field="Task Name", message="Task name is required.")
        if len(value) > self.TASK_TITLE_MAX_LEN:
            raise TaskValidationError(field="Task Name", message=f"Task name must be at most {self.TASK_TITLE_MAX_LEN} characters.")
        self._title = value 

    def set_seconds_in_focus_per_day(self, seconds):
        if not isinstance(seconds, (int, float)):
            raise TaskValidationError(field="seconds", message="O valor deve ser um número (int ou float).")
        if seconds <= 0:
            raise TaskValidationError(field="seconds", message="O valor deve ser maior que 0.")
    
        today = str(date.today()) 
        self._seconds_in_focus_per_day[today] = seconds

    def to_dict(self):
        return {
            "user_FK": self.__user_FK,
            "identificator": self.__identificator,
            "title": self._title,
            "color": self._color,
            "status": self._status,
            "seconds_in_focus_per_day": self._seconds_in_focus_per_day,
        }
