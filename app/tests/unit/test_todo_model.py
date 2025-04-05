import pytest
from datetime import datetime, timedelta
from app.models.todo import ToDo
from app.models.exceptions import ToDoValidationError

def test_todo_initialization():
    todo = ToDo(title="Buy groceries", identificator="123", task_FK=1)
    
    assert todo.title == "Buy groceries"
    assert todo.identificator == "123"
    assert todo.task_FK == 1
    assert todo.status == "in progress"
    assert isinstance(datetime.fromisoformat(todo.created_time), datetime)
    assert todo.completed_time is None
    
def test_title_validation():
    with pytest.raises(ToDoValidationError, match="To-do name is required."):
        ToDo(title="", identificator="123", task_FK=1)

def test_todo_status_validation():
    todo = ToDo(title="Finish report", identificator="456", task_FK=2)
    
    with pytest.raises(ToDoValidationError, match="Invalid Status. Choose one: in progress, completed, deleted."):
        todo.status = "invalid_status"

def test_todo_mark_as_completed():
    todo = ToDo(title="Workout", identificator="789", task_FK=3)
    todo.mark_as_completed()
    
    assert todo.status == "completed"
    assert isinstance(datetime.fromisoformat(todo.completed_time), datetime)

def test_todo_mark_as_in_progress():
    todo = ToDo(title="Read a book", identificator="321", task_FK=4)
    todo.mark_as_completed()
    assert todo.status == "completed"
    assert todo.completed_time is not None
    
    todo.mark_as_in_progress()
    assert todo.status == "in progress"
    assert todo.completed_time is None

def test_todo_mark_as_deleted():
    todo = ToDo(title="Clean the house", identificator="654", task_FK=5)
    todo.mark_as_deleted()
    
    assert todo.status == "deleted"

def test_todo_created_time_format():
    todo = ToDo(title="Write code", identificator="987", task_FK=6)
    expected_format = datetime.now().strftime("%m-%d-%Y %H:%M")
    assert todo.created_time_formatted == expected_format

def test_todo_completed_time_format():
    completed_time = (datetime.now() - timedelta(days=1)).isoformat()
    todo = ToDo(title="Submit assignment", identificator="753", task_FK=7, completed_time=completed_time)
    expected_format = (datetime.now() - timedelta(days=1)).strftime("%m-%d-%Y %H:%M")
    assert todo.completed_time_formatted == expected_format

def test_todo_to_dict():
    todo = ToDo(title="Cook dinner", identificator="852", task_FK=8)
    todo_dict = todo.to_dict()
    
    assert todo_dict == {
        "task_FK": 8,
        "title": "Cook dinner",
        "identificator": "852",
        "status": "in progress",
        "created_time": todo.created_time,
        "completed_time": None
    }
