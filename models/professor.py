class Professor:
    def __init__(self, professor_id, name, department, 
                 courses=None, preferences=None, max_hours=12,
                 unavailable_times=None, office_location=None):
        self.professor_id = professor_id
        self.name = name
        self.department = department
        self.courses = courses or []
        self.preferences = preferences or {
            "preferred_days": ["Monday", "Wednesday", "Friday"],
            "preferred_times": ["morning"],
            "max_consecutive_classes": 2,
            "avoid_gaps": True
        }
        self.max_hours = max_hours
        self.unavailable_times = unavailable_times or {}
        self.office_location = office_location
        
        # Current schedule
        self.schedule = {}  # {day: [(time_slot, course_id, room_id)]}
        self.total_hours = 0
    
    def __str__(self):
        return f"{self.name} ({self.department})"
    
    def __repr__(self):
        return f"Professor({self.professor_id})"
    
    def can_teach(self, course_id):
        return course_id in self.courses
    
    def is_available(self, day, time_slot):

        # Check unavailable times
        if day in self.unavailable_times:
            if time_slot in self.unavailable_times[day]:
                return False
        
        # Check if already teaching
        if day in self.schedule:
            for slot_info in self.schedule[day]:
                if slot_info[0] == time_slot:  # slot_info = (time_slot, course_id, room_id)
                    return False
        
        return True
    
    def assign_course(self, day, time_slot, course_id, room_id):

        if day not in self.schedule:
            self.schedule[day] = []
        
        self.schedule[day].append((time_slot, course_id, room_id))
        self.total_hours += 1.5  # Assuming 1.5 hour slots
        
        # Sort schedule by time
        self.schedule[day].sort(key=lambda x: x[0])
    
    def get_preference_score(self, day, time_slot):

        score = 0
        
        # Day preference
        if day in self.preferences.get("preferred_days", []):
            score += 2
        
        # Time preference
        time_of_day = "morning" if time_slot <= 2 else "afternoon"  # Assuming slots 0-5
        if time_of_day in self.preferences.get("preferred_times", []):
            score += 1
        
        # Avoid consecutive classes check
        if self.preferences.get("avoid_gaps", True):
            if day in self.schedule:
                last_slot = self.schedule[day][-1][0] if self.schedule[day] else -1
                if time_slot == last_slot + 1:
                    score += 1  # Prefer consecutive classes
        
        return score
    
    def is_overloaded(self):
        return self.total_hours > self.max_hours