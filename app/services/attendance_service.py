"""
Business Logic for Attendance Management
Handles R005-R006: Attendance validation rules
"""

from datetime import date
from sqlalchemy.orm import Session


class AttendanceService:
    """
    R005: Attendance can only be marked for current/past dates
    R006: Supervisor can only mark attendance for their assigned site
    """

    @staticmethod
    def validate_attendance_date(attendance_date: date) -> bool:
        """
        R005: Prevent future date attendance marking
        """
        today = date.today()
        return attendance_date <= today

    @staticmethod
    def can_mark_site_attendance(
        db: Session, supervisor_user_id: int, site_id: int
    ) -> bool:
        """
        R006: Check if supervisor is assigned to this site
        TODO: Implement after SiteSupervisor model is ready
        """
        # Placeholder: Query SiteSupervisors table
        return True
