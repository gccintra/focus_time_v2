from dataclasses import dataclass, field 
from typing import List, Optional
from app.models.project import Project
from app.models.task import Task
from app.models.focus_session import FocusSession


@dataclass
class ProjectDetailsDTO:
    project: Optional[Project] = None
    tasks: List[Task] = field(default_factory=list)
    focus_sessions: List[FocusSession] = field(default_factory=list)

