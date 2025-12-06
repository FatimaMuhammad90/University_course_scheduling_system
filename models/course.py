# models/course.py - ADD THIS METHOD
class course:
    def __init__(self, course_id, name, department, credits, 
                 students, course_type, professors=None, 
                 prerequisites=None, preferred_times=None,
                 required_rooms=None, duration=1.5):
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
        self.assigned_time = None
        self.assigned_room = None
        self.assigned_professor = None
        self.assigned_day = None
    
    def __str__(self):
        return f"{self.course_id}: {self.name} ({self.students} students)"
    
    def __repr__(self):
        return f"course({self.course_id})"
    
    # ADD THIS METHOD - it was missing
    def get_requirements(self):
        """Get room requirements based on course type"""
        requirements = []
        if self.course_type == "lab":
            requirements.append("computers")
            requirements.append("lab_equipment")
        elif self.course_type == "lecture":
            requirements.append("projector")
            if self.students > 100:
                requirements.append("microphone")
        
        if self.required_rooms:
            requirements.extend(self.required_rooms)
        return requirements
    
    def has_conflict_with(self, other_course):
        """Check if this course conflicts with another course"""
        if not self.assigned_time or not other_course.assigned_time:
            return False
        
        if (self.assigned_day == other_course.assigned_day and 
            self.assigned_time == other_course.assigned_time):
            
            if (self.assigned_professor and other_course.assigned_professor and
                self.assigned_professor.professor_id == other_course.assigned_professor.professor_id):
                return True
            
            if self.department == other_course.department:
                return True
        
        return False