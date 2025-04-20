from typing import List, Dict, Any 
from datetime import date, timedelta, datetime

from app.models import user
from app.models.dtos.project_dto import ProjectDetailsDTO

from ..models.project import Project 
from ..models.exceptions import ProjectNotFoundError, ProjectValidationError, DatabaseError, UserNotFoundError
from ..infra.repository.project_repository import ProjectRepository
from ..utils.logger import logger



def format_hour_minute(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes = round(remainder / 60)
    return f"{hours:02}h{minutes:02}m"


def format_hour_minute_second(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


class ProjectService:
    def __init__(self):
        self.repo = ProjectRepository()
        # You might need a FocusSessionRepository if you need more complex session queries later
        # self.focus_session_repo = FocusSessionRepository()

    def get_all_projects_per_user(self, user_id=None):
        logger.debug(f"Service: Getting all projects for user '{user_id}'")
        try:
            projects = self.repo.get_all_by_user(user_identificator=user_id)
            # projects.sort(key=lambda p: p.title)
            return projects
        except DatabaseError as e:
            logger.error(f"Service: Database error getting projects for user '{user_id}': {e}", exc_info=True)
            raise 

    def create_new_project(self, title: str, color: str, user_id: str) -> Project:
        logger.info(f"Service: Attempting to create project '{title}' for user '{user_id}'")
        try:
            new_project = Project(title=title, color=color, user_identificator=user_id)
            self.repo.add(new_project)
            self.repo._session.commit()

            logger.info(f"Service: Project '{title}' (ID: {new_project.identificator}) created successfully for user '{user_id}'.")
            return new_project

        except ProjectValidationError as e:
            self.repo._session.rollback() 
            logger.warning(f"Service: Project creation validation failed for user '{user_id}': {e}")
            raise 
        except (DatabaseError, Exception) as e:
            self.repo._session.rollback() 
            logger.error(f"Service: Error creating project '{title}' for user '{user_id}': {e}", exc_info=True)
            raise DatabaseError(f"Could not create project '{title}'.")


    def get_by_id(self, project_id: str, user_id: str) -> ProjectDetailsDTO:
        logger.debug(f"Service: Getting project by id '{project_id}' for user '{user_id}'")
        try:
            project = self.repo.get_by_id(project_identificator=project_id, user_identificator=user_id)
            if project is None:
                logger.warning(f"Service: Project not found for id '{project_id}' and user '{user_id}'.")
                raise ProjectNotFoundError(project_id=project_id) # Raise error if not found
            return project
        except (ProjectNotFoundError, DatabaseError) as e:
             raise
        except Exception as e:
            logger.error(f"Service: Unexpected error getting project '{project_id}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while retrieving project '{project_id}'.")
        

    def get_details_for_project_room(self, project_id: str, user_id: str) -> Dict[str, Any]:
        logger.debug(f"Service: Getting project details for frontend - id '{project_id}' for user '{user_id}'")
        try:
            project_details_dto = self.repo.get_by_id(
                project_identificator=project_id,
                user_identificator=user_id
            )

            if not project_details_dto.project:
                logger.warning(f"Service: Project not found for id '{project_id}' and user '{user_id}'.")
                raise ProjectNotFoundError(project_id=project_id)

            response_data = {}

            response_data["project"] = {
                "identificator": project_details_dto.project.identificator,
                "title": project_details_dto.project.title,
                "color": project_details_dto.project.color,
                "active": project_details_dto.project.active,
            }

            # Dados das Tarefas
            response_data["tasks"] = [
                {
                    "identificator": task.identificator,
                    "title": task.title,
                    "description": task.description,
                    # Acessa o nome do objeto de status associado
                    "status": task.status.name if task.status else "N/A",
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                } for task in project_details_dto.tasks
            ]

            response_data["focus_sessions"] = [
                {
                    "id": session.id,
                    "started_at": session.started_at.isoformat(),
                    "duration_seconds": session.duration_seconds,
                    "end_time": session.end_time.isoformat(),
                } for session in project_details_dto.focus_sessions
            ]

            today = date.today()
            today_total_seconds = sum(
                session.duration_seconds
                for session in project_details_dto.focus_sessions
                if session.started_at.date() == today
            )
            response_data["today_focus_time_formatted"] = format_hour_minute_second(today_total_seconds)
            response_data["today_focus_total_seconds"] = today_total_seconds # Pode ser útil ter os segundos também

            logger.info(f"Service: Successfully prepared project details for frontend - id '{project_id}'")
            return response_data

        except (ProjectNotFoundError, DatabaseError, UserNotFoundError) as e:
            logger.warning(f"Service: Error getting project details for frontend - id '{project_id}': {e}")
            raise
        except Exception as e:
            logger.error(f"Service: Unexpected error preparing project details for frontend - id '{project_id}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while preparing details for project '{project_id}'.")





# ====================================================================================================================================

    def get_projects_with_time_summary(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Service: Calculating time summaries per project for user '{user_id}'")
        projects_summary = []
        try:
            projects_db = self.repo.get_projects_with_focus_sessions_by_user(user_identificator=user_id)

            today = date.today()
            days_since_sunday = (today.weekday() + 1) % 7
            start_of_week = today - timedelta(days=days_since_sunday) 
            logger.debug(f"Service: Calculating summaries for today ({today}) and week starting {start_of_week}")

            for project_db in projects_db:
                today_total_seconds = 0
                week_total_seconds = 0

                for focus_session_db in project_db.focus_sessions:
                    session_date = focus_session_db.started_at.date()

                    if session_date == today:
                        today_total_seconds += focus_session_db.duration_seconds

                    if session_date >= start_of_week:
                        week_total_seconds += focus_session_db.duration_seconds

                today_total_minutes = today_total_seconds // 60
                week_total_minutes = week_total_seconds // 60

                projects_summary.append({
                    "identificator": project_db.identificator,
                    "title": project_db.title,
                    "color": project_db.color,
                    "today_total_time": format_hour_minute(today_total_seconds),
                    "week_total_time": format_hour_minute(week_total_seconds),
                    "today_total_minutes": today_total_minutes,
                    "week_total_minutes": week_total_minutes
                })
                logger.debug(f"Service: Project '{project_db.title}' ({project_db.identificator}) - Today: {today_total_minutes}m, Week: {week_total_minutes}m")

            #projects_summary.sort(key=lambda x: x["title"])

            logger.info(f"Service: Successfully calculated time summaries for {len(projects_summary)} projects for user '{user_id}'")
            return projects_summary

        except DatabaseError as e:
            logger.error(f"Service: Database error calculating project time summaries for user '{user_id}': {e}")
            raise
        except Exception as e:
            logger.error(f"Service: Unexpected error calculating project time summaries for user '{user_id}': {e}")
            raise DatabaseError(f"An unexpected error occurred while preparing project summaries for user {user_id}.")


    def get_data_for_last_365_days_home_chart(self, user_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Service: Calculating daily focus minutes (365 days) for user '{user_id}'")
        minutes_per_day: Dict[date, int] = {}
        try:
            projects_db = self.repo.get_projects_with_focus_sessions_by_user(user_identificator=user_id)

            today = date.today()
            start_date = today - timedelta(days=365)
            logger.debug(f"Service: Calculating heatmap data from {start_date} to {today}")

            for project_db in projects_db:
                for fs in project_db.focus_sessions:
                    session_date = fs.started_at.date()
                   
                    if session_date >= start_date:
                        minutes = fs.duration_seconds // 60
                        minutes_per_day[session_date] = minutes_per_day.get(session_date, 0) + minutes

            heatmap_data = [
                {"date": d.isoformat(), "count": m}
                for d, m in minutes_per_day.items()
            ]

            heatmap_data.sort(key=lambda x: x["date"])

            logger.info(f"Service: Prepared {len(heatmap_data)} daily entries for heatmap for user '{user_id}'")
            return heatmap_data

        except DatabaseError as e:
            logger.error(f"Service: Database error calculating heatmap data for user '{user_id}': {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Service: Unexpected error calculating heatmap data for user '{user_id}': {e}", exc_info=True)
            raise DatabaseError(f"An unexpected error occurred while preparing heatmap data for user {user_id}.")

