# models/professor.py
class professor:
    def __init__(
        self,
        professor_id,
        name,
        department,
        courses=None,
        preferences=None,
        max_hours=12,
        unavailable_times=None,
        office_location=None,
    ):
        self.professor_id = professor_id
        self.name = name
        self.department = department
        self.courses = courses or []
        self.preferences = preferences or {
            "preferred_days": ["monday", "wednesday", "friday"],
            "preferred_times": ["morning"],
            "max_consecutive_classes": 2,
            "avoid_gaps": True,
        }
        self.max_hours = max_hours
        self.unavailable_times = unavailable_times or {}
        self.office_location = office_location
        self.schedule = {}
        self.total_hours = 0

    def __str__(self):
        return f"{self.name} ({self.department})"

    def __repr__(self):
        return f"professor({self.professor_id})"

    def can_teach(self, course_id):
        """Check if professor can teach a course."""
        return course_id in self.courses

    def is_available(self, day, time_slot):
        """Check if professor is available at given time."""
        if day in self.unavailable_times:
            if time_slot in self.unavailable_times[day]:
                return False

        if day in self.schedule:
            for slot_info in self.schedule[day]:
                if slot_info[0] == time_slot:
                    return False

        return True

    def assign_course(self, day, time_slot, course_id, room_id):
        """Assign a course to professor's schedule."""
        if day not in self.schedule:
            self.schedule[day] = []

        self.schedule[day].append((time_slot, course_id, room_id))
        self.total_hours += 1.5
        self.schedule[day].sort(key=lambda x: x[0])

    def get_preference_score(self, day, time_slot):
        """Calculate how much professor prefers this time."""
        score = 0

        if day in self.preferences.get("preferred_days", []):
            score += 2

        time_of_day = "morning" if time_slot <= 2 else "afternoon"
        if time_of_day in self.preferences.get("preferred_times", []):
            score += 1

        if self.preferences.get("avoid_gaps", True):
            if day in self.schedule:
                last_slot = self.schedule[day][-1][0] if self.schedule[day] else -1
                if time_slot == last_slot + 1:
                    score += 1

        return score

    def is_overloaded(self):
        """Check if professor is over maximum hours."""
        return self.total_hours > self.max_hours
