from flask import jsonify, render_template, abort
from app.services.focus_session_service import FocusSessionService
from ..models.exceptions import AuthorizationError, DatabaseError, FocusSessionValidationError, ProjectNotFoundError, ProjectValidationError
from ..utils.logger import logger

class FocusSessionController:
    def __init__(self):
        self.service = FocusSessionService()

    def save_focus_session(self, user_id, data):

        # Validar campos e tipos antes de salvar em banco.
        started_at = data.get('started_at')
        duration_seconds = data.get('duration_seconds')
        project_id = data.get('project_id')



        try:
            self.service.save_focus_session(project_id=project_id, user_id=user_id, started_at=started_at, duration_seconds=duration_seconds)
            return jsonify({
                "success": True,
                "message": "The seconds have been saved.",
                "data": None,
                "error": None
            }), 200
        except (ValueError, FocusSessionValidationError, ProjectValidationError) as e:
            logger.warning(f"Controller: Validation error saving session for user '{user_id}'. Type: {type(e).__name__}. Reason: {e}")
            return jsonify({
                "success": False,
                "message": f"Invalid request data: {str(e)}",
                "data": None,
                "error": {
                    "code": 400,
                    "type": type(e).__name__, # Ex: "ValueError", "FocusSessionValidationError"
                    "details": str(e)
                }
            }), 400

        except ProjectNotFoundError as e:
            logger.warning(f"Controller: Project not found error saving session for user '{user_id}'. Reason: {e}")
            return jsonify({
                "success": False,
                "message": str(e),
                "data": None,
                "error": {
                    "code": 404,
                    "type": "ProjectNotFoundError",
                    "details": str(e)
                }
            }), 404

        except AuthorizationError as e:
            logger.error(f"Controller: Authorization error saving session for user '{user_id}'. Reason: {e}") 
            return jsonify({
                "success": False,
                "message": "Permission denied to access the specified project.",
                "data": None,
                "error": {
                    "code": 403,
                    "type": "AuthorizationError",
                    "details": str(e) 
                }
            }), 403

        except DatabaseError as e:
            logger.error(f"Controller: Database error saving session for user '{user_id}'. Reason: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "A database error occurred while saving the session.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "DatabaseError",
                    "details": "Internal database error." 
                }
            }), 500

        except Exception as e:
            logger.error(f"Controller: Unexpected error saving session for user '{user_id}'. Reason: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "message": "An unexpected internal server error occurred.",
                "data": None,
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "details": "An unexpected error occurred." # Não expor detalhes
                }
            }), 500
