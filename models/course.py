class Course:
    def __init__(self, course_id, name, department, credits, students, course_type, professors=None, prerequisites=None, preferred_times=None, required_rooms=None, duration=1.5):
        self.course_id = course_id
        self.name = name
        self.department = department
        self.credits = credits
        self.students = students
        self.course_type = course_type
        self.professors = professors or []
        self.prerequisites = prerequisites or []
        self.preferred_times = preferred_times or []
        self.required_rooms = required_rooms or []
        self.duration = duration
        # scheduling information (filled during scheduling)
        self.assigned_time = None
        self.assigned_room = None
        self.assigned_professor = None
        self.assigned_day = None

    def __str__(self):
        return f"{self.course_id}: {self.name} ({self.students} students)"
    
    def __repr__(self):
        requirements = []

        if self.course_type == "lab":
            requirements.append("has_computers")
            requirements.append("has_lab_equipment") 
        elif self.course_type == "lecture":
            requirements.append("has_projector")
            if self.students > 100:
                requirements.append("has_microphone")
       
        requirements.extend(self.required_rooms)
        return requirements
    

    def has_confilct_with(self, other_course):
        if not self.assigned_time or not other_course.assigned_time:
            return False
            
        # Same time slot conflict
        if (self.assigned_day == other_course.assigned_day and self.assigned_time == other_course.assigned_time):
            
            # Check for professor conflict
            if (self.assigned_professor and other_course.assigned_professor and self.assigned_professor == other_course.assigned_professor):
                return True
            
            # Check for student conflict 
            if self.department == other_course.department:
                return True 