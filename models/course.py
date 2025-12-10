# models/course.py
class course:
    def __init__(
        self,
        course_id,
        name,
        department,
        credits,
        students,
        course_type,
        professors=None,
        prerequisites=None,
        preferred_times=None,
        required_rooms=None,
        duration=1.5,
    ):
        self.course_id = course_id
        self.name = name
        self.department = department
        self.credits = credits
        self.students = students
        # normalize type
        self.course_type = course_type.lower() if course_type else None
        self.professors = professors or []
        self.prerequisites = prerequisites or []
        self.preferred_times = preferred_times or []
        self.required_rooms = required_rooms or []
        self.duration = duration

        self.assigned_time = None
        self.assigned_room = None
        self.assigned_professor = None
        self.assigned_day = None

    def __str__(self):
        return f"{self.course_id}: {self.name} ({self.students} students)"

    def __repr__(self):
        return f"course({self.course_id})"

    def get_requirements(self):
        requirements = []
        ctype = (self.course_type or "").lower()

        if ctype == "lab":
            # keep this simple and compatible with your JSON
            requirements.append("computers")
        elif ctype == "lecture":
            requirements.append("projector")
            if self.students > 100:
                requirements.append("microphone")

        # room-specific constraints
        if self.required_rooms:
            requirements.extend(self.required_rooms)

        return requirements

    def has_conflict_with(self, other_course):
        if self.assigned_time is None or other_course.assigned_time is None:
            return False

        if (
            self.assigned_day == other_course.assigned_day
            and self.assigned_time == other_course.assigned_time
        ):
            if (
                self.assigned_professor
                and other_course.assigned_professor
                and self.assigned_professor.professor_id
                == other_course.assigned_professor.professor_id
            ):
                return True

            if self.department == other_course.department:
                return True

        return False
