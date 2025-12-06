# algorithms/ucs.py - FIXED VERSION
import heapq
import config
from models import schedule

class ucs:
    def __init__(self, schedule_obj):
        self.schedule = schedule_obj
        self.priority_queue = []
        self.node_counter = 0  # For tie-breaking
    
    def find_min_cost_schedule(self):
        """Uniform Cost Search for minimum cost schedule"""
        print("Starting Uniform Cost Search...")
        
        # Start node
        start_node = self.schedule.copy()
        start_cost = 0
        start_node.calculate_fitness()
        
        # Priority queue: (cost, counter, schedule, assignments_made)
        # Counter ensures we can compare when costs are equal
        self.node_counter = 0
        heapq.heappush(self.priority_queue, 
                      (start_cost, self.node_counter, start_node, []))
        self.node_counter += 1
        
        visited = set()
        nodes_expanded = 0
        
        while self.priority_queue:
            current_cost, _, current_sched, assignments = heapq.heappop(self.priority_queue)
            nodes_expanded += 1
            
            if nodes_expanded % 100 == 0:
                print(f"\rUCS: Cost {current_cost:.1f}, Queue: {len(self.priority_queue)}, "
                      f"Nodes: {nodes_expanded}", end="")
            
            # Check if complete
            if len(assignments) == len(current_sched.courses):
                if current_sched.is_valid():
                    print(f"\n✅ UCS found minimum cost solution")
                    print(f"   Cost: {current_cost:.2f}, Nodes: {nodes_expanded}")
                    print(f"   Fitness: {current_sched.calculate_fitness():.2f}")
                    return current_sched
            
            # Generate successors
            for successor, cost_increase in self.generate_successors(current_sched, assignments):
                new_cost = current_cost + cost_increase
                
                state_id = self.get_state_id(successor)
                if state_id in visited:
                    continue
                visited.add(state_id)
                
                new_assignments = assignments + [{
                    'course': next_course.course_id if 'next_course' in locals() else '',
                    'room': '',
                    'prof': '',
                    'day': '',
                    'time': ''
                }]
                
                heapq.heappush(self.priority_queue, 
                              (new_cost, self.node_counter, successor, new_assignments))
                self.node_counter += 1
        
        print(f"\n❌ UCS could not find solution")
        return None
    
    def generate_successors(self, schedule_obj, assignments):
        """Generate successor states with their costs"""
        successors = []
        
        # Find next course to schedule
        scheduled_courses = {a['course'] for a in assignments if a['course']}
        next_course = None
        
        for course in schedule_obj.courses:
            if course.course_id not in scheduled_courses:
                next_course = course
                break
        
        if not next_course:
            return successors
        
        # Generate all assignments for this course
        for room in schedule_obj.rooms:
            if not room.can_accommodate(next_course):
                continue
            
            for prof in schedule_obj.professors:
                if not prof.can_teach(next_course.course_id):
                    continue
                
                for day in config.DAYS:
                    for time_slot in range(len(config.TIME_SLOTS)):
                        if not (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                            continue
                        
                        # Calculate cost of this assignment
                        cost = self.calculate_assignment_cost(next_course, room, prof, 
                                                             day, time_slot)
                        
                        # Create new schedule
                        new_sched = schedule_obj.copy()
                        
                        new_course = next((c for c in new_sched.courses 
                                         if c.course_id == next_course.course_id), None)
                        new_room = next((r for r in new_sched.rooms 
                                       if r.room_id == room.room_id), None)
                        new_prof = next((p for p in new_sched.professors 
                                       if p.professor_id == prof.professor_id), None)
                        
                        if new_course and new_room and new_prof:
                            new_sched.add_assignment(new_course, new_room, new_prof, 
                                                   day, time_slot)
                            successors.append((new_sched, cost))
        
        return successors
    
    def calculate_assignment_cost(self, course, room, professor, day, time_slot):
        """Calculate cost of a single assignment"""
        cost = 0
        
        # Room cost
        cost += room.cost_per_hour * course.duration
        
        # Time preference cost
        time_of_day = "morning" if time_slot <= 2 else "afternoon"
        if time_of_day not in course.preferred_times:
            cost += 50  # Penalty for non-preferred time
        
        # Professor preference cost
        try:
            pref_score = professor.get_preference_score(day, time_slot)
            cost += (10 - pref_score) * 5  # Lower preference = higher cost
        except:
            pass  # If method doesn't exist
        
        # Room utilization cost
        try:
            utilization = course.students / room.capacity
            if utilization < 0.3:
                cost += 30  # Penalty for underutilization
        except:
            pass
        
        return cost
    
    def get_state_id(self, schedule_obj):
        assignments = []
        for course in schedule_obj.courses:
            if course.assigned_time is not None:
                assignments.append(f"{course.course_id}:{course.assigned_day}:{course.assigned_time}")
        assignments.sort()
        return "|".join(assignments)