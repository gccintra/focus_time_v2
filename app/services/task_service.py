from ..models.task import Task
from ..models.exceptions import TaskNotFoundError, TaskValidationError
from ..repository.task_record import TaskRecord
from ..utils.logger import logger
from ..models.exceptions import DatabaseError
from datetime import date, timedelta


class TaskService:
    def __init__(self):
        try:
            self.task_db = TaskRecord()
        except ValueError as e:
            logger.error(f"Erro ao inicializar TaskRecord: {e}")
            raise DatabaseError("Erro ao inicializar o banco de dados.")

    def get_all_tasks(self, user_id=None):
        tasks = self.task_db.get_models(user_id=user_id)

        sorted_tasks = sorted(tasks, key=lambda task: task.week_total_minutes, reverse=True)
        return sorted_tasks

      
    def get_data_for_all_charts(self, user_id):
        tasks_data = self.task_db.get_models(user_id=user_id)
        tasks_for_charts = []

        for task in tasks_data:
            # if task.week_total_minutes > 0:  
                tasks_for_charts.append({
                    "identificator": task.identificator,
                    "title": task.title,
                    "color": task.color,
                    "minutes": task.week_total_minutes
                })

        tasks_for_charts.sort(key=lambda x: x["minutes"], reverse=False)
        return tasks_for_charts

    def create_new_task(self, name, color, user_id):
        try:         
            identificator = self.task_db.generate_unique_id()
            new_task = Task(identificator=identificator, title=name, color=color, user_FK=user_id)
            self.task_db.write(new_task)
            logger.info(f'Task {name} criada com sucesso!')
            return new_task
        except TaskValidationError as e:
            logger.warning(f"Task creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating task '{name}': {str(e)}")
            raise
       
    def update_task_time(self, task_id, elapsed_seconds, user_id):
        try:
            task = self.get_task_by_id(task_id, user_id)
            task.set_seconds_in_focus_per_day(elapsed_seconds)
            self.task_db.save()
        except TaskValidationError as e:
            logger.error(f"Erro ao salvar tempo de foco diário para a task '{task.identificator}: {str(e)}")
            raise
        except (TaskNotFoundError, Exception):   
            logger.error(f"Erro ao salvar tempo de foco diário para a task '{task.identificator}")
            raise
    
    def get_task_by_id(self, task_id, user_id=None):
        try:
            return self.task_db.get_task_by_id(task_id=task_id, user_id=user_id)
        except (TaskNotFoundError, Exception):
            raise

 
    def get_data_for_last_365_days_home_chart(self, user_id):
        tasks_data = self.task_db.get_models(user_id=user_id)
        minutes_per_day = {}

        for task in tasks_data:
            for date, seconds in task.seconds_in_focus_per_day.items():
                minutes = seconds // 60  
                if date in minutes_per_day:
                    minutes_per_day[date] += minutes  
                else:
                    minutes_per_day[date] = minutes  

        minutes_per_day = [{"date": date, "count": count} for date, count in minutes_per_day.items()]
        return minutes_per_day





        # tasks_data = self.task_db.get_models()
        # minutes_per_day = []
       
        # for task in tasks_data:
        #     for day in task.seconds_in_focus_per_day:
        #         for minute_day in minutes_per_day:
        #             if day == minute_day['date']:
        #                 minute_in_array = int(minute_day['count'])
        #                 minute_in_task = int(round(task.seconds_in_focus_per_day[day] / 60.0))
        #                 minute_day['count'] = minute_in_array + minute_in_task
        #                 break
        #         else:
        #             minutes = round(task.seconds_in_focus_per_day[day] / 60.0)

        #             minutes_per_day.append({
        #                 'date': day,
        #                 'count': minutes
        #             })
    
        
        # return minutes_per_day


