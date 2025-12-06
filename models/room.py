# models/room.py
class room:
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
        self.schedule = {}
        self.utilization = 0
    
    def __str__(self):
        return f"{self.room_id}: {self.name} (Cap: {self.capacity})"
    
    def __repr__(self):
        return f"room({self.room_id})"
    
    def is_available(self, day, time_slot):
        """Check if room is available at given time"""
        if day in self.maintenance_schedule:
            if time_slot in self.maintenance_schedule[day]:
                return False
        
        if day in self.schedule:
            if time_slot in self.schedule[day]:
                return False
        
        return True
    
    def book(self, day, time_slot, course_id):
        """Book the room for a specific time"""
        if day not in self.schedule:
            self.schedule[day] = {}
        
        if time_slot in self.schedule[day]:
            return False  # Already booked
        
        self.schedule[day][time_slot] = course_id
        return True
    
    def can_accommodate(self, course):
        """Check if room can accommodate a course"""
        # Check capacity
        if course.students > self.capacity:
            return False
        
        # Check features - FIXED: handle missing get_requirements
        try:
            required_features = course.get_requirements()
        except AttributeError:
            # If course doesn't have get_requirements, use default
            if course.course_type == "lab":
                required_features = ["computers", "lab_equipment"]
            elif course.course_type == "lecture":
                required_features = ["projector"]
            else:
                required_features = []
        
        for feature in required_features:
            if feature not in self.features:
                return False
        
        # Check room type compatibility
        if course.course_type == "lab" and self.room_type != "lab":
            return False
        
        return True
    
    def get_utilization(self, total_time_slots):
        """Calculate utilization percentage"""
        booked_slots = 0
        for day_slots in self.schedule.values():
            booked_slots += len(day_slots)
        
        if total_time_slots > 0:
            self.utilization = (booked_slots / total_time_slots) * 100
        return self.utilization