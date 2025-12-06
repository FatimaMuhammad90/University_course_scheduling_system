class Room:
    def __init__(self, room_id, name, capacity, room_type, 
                 features=None, building=None, floor=None,
                 maintenance_schedule=None, cost_per_hour=0):
        
        self.room_id = room_id
        self.name = name
        self.capacity = capacity
        self.room_type = room_type
        self.features = features or []
        self.building = building
        self.floor = floor
        self.maintenance_schedule = maintenance_schedule or {}
        self.cost_per_hour = cost_per_hour
        
        # Scheduling information
        self.schedule = {}  # {day: {time_slot: course_id}}
        self.utilization = 0  # Percentage of time used
    
    def __str__(self):
        return f"{self.room_id}: {self.name} (Cap: {self.capacity}, Type: {self.room_type})"
    
    def __repr__(self):
        return f"Room({self.room_id})"
    
    def is_available(self, day, time_slot):
        # Check maintenance schedule
        if day in self.maintenance_schedule:
            if time_slot in self.maintenance_schedule[day]:
                return False
        
        # Check if already booked
        if day in self.schedule:
            if time_slot in self.schedule[day]:
                return False
        
        return True
    
    def book(self, day, time_slot, course_id):
        if day not in self.schedule:
            self.schedule[day] = {}
        
        self.schedule[day][time_slot] = course_id
        return True
    
    def can_accommodate(self, course):
        """Check if room can accommodate a course"""
        # Check capacity
        if course.students > self.capacity:
            return False
        
        # Check features
        required_features = course.get_requirements()
        for feature in required_features:
            if feature not in self.features:
                return False
        
        # Check room type compatibility
        if course.course_type == "lab" and self.room_type != "lab":
            return False
        
        return True
    
    def get_utilization(self, total_time_slots):
        booked_slots = sum(len(day_slots) for day_slots in self.schedule.values())
        self.utilization = (booked_slots / total_time_slots) * 100
        return self.utilization