import pytest
from datetime import date, timedelta
from app.models.task import Task
from app.models.exceptions import TaskValidationError

def test_task_initialization():
    task = Task(user_FK=1, identificator="123", title="Study Python", color="blue")
    
    assert task.user_FK == 1
    assert task.identificator == "123"
    assert task.title == "Study Python"
    assert task.color == "blue"
    assert task.status == "active"
    assert task.seconds_in_focus_per_day == {}

def test_title_validation():
    with pytest.raises(TaskValidationError, match="Task name is required."):
        Task(user_FK=1, identificator="123", title="", color="blue")
    
    with pytest.raises(TaskValidationError, match="Task name must be at most 30 characters."):
        Task(user_FK=1, identificator="123", title="A" * 31, color="blue")

def test_today_total_seconds():
    today = str(date.today())
    task = Task(user_FK=1, identificator="123", title="Exercise", color="red", seconds_in_focus_per_day={today: 3600})
    
    assert task.today_total_seconds == 3600

def test_today_total_minutes():
    today = str(date.today())
    task = Task(user_FK=1, identificator="123", title="Read", color="green", seconds_in_focus_per_day={today: 3600})
    
    assert task.today_total_minutes == 60.0

def test_today_total_time():
    today = str(date.today())
    task = Task(user_FK=1, identificator="123", title="Read", color="green", seconds_in_focus_per_day={today: 3660})
    
    assert task.today_total_time == "01h01m"

def test_today_total_time_timer():
    today = str(date.today())
    task = Task(user_FK=1, identificator="123", title="Read", color="green", seconds_in_focus_per_day={today: 3661})
    
    assert task.today_total_time_timer == "01:01:01"

def test_week_total_seconds():
    today = date.today()
    week_data = {(today - timedelta(days=i)).isoformat(): (i + 1) * 100 for i in range(7)}
    task = Task(user_FK=1, identificator="123", title="Work", color="black", seconds_in_focus_per_day=week_data)
    
    assert task.week_total_seconds == sum(week_data.values())

def test_week_total_minutes():
    today = date.today()
    week_data = {(today - timedelta(days=i)).isoformat(): (i + 1) * 100 for i in range(7)}
    task = Task(user_FK=1, identificator="123", title="Work", color="black", seconds_in_focus_per_day=week_data)
    
    assert task.week_total_minutes == round(sum(week_data.values()) / 60.0)

def test_week_total_time():
    today = date.today()
    week_data = {(today - timedelta(days=i)).isoformat(): 523 for i in range(7)}
    task = Task(user_FK=1, identificator="123", title="Work", color="black", seconds_in_focus_per_day=week_data)

    assert task.week_total_time == "01h01m"

def test_set_seconds_in_focus_per_day():
    task = Task(user_FK=1, identificator="123", title="Meditate", color="yellow")
    
    task.set_seconds_in_focus_per_day(3000)
    today = str(date.today())
    assert task.seconds_in_focus_per_day[today] == 3000
    
    with pytest.raises(TaskValidationError, match=r"O valor deve ser um número \(int ou float\)\."):
        task.set_seconds_in_focus_per_day("not a number")
    
    with pytest.raises(TaskValidationError, match=r"O valor deve ser maior que 0\."):
        task.set_seconds_in_focus_per_day(0)

def test_to_dict():
    task = Task(user_FK=1, identificator="123", title="Workout", color="purple")
    task_dict = task.to_dict()
    
    assert task_dict == {
        "user_FK": 1,
        "identificator": "123",
        "title": "Workout",
        "color": "purple",
        "status": "active",
        "seconds_in_focus_per_day": {},
    }
