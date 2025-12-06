# algorithms/a_star.py - FIXED VERSION
import heapq
import config
from models import schedule

class a_star:
    def __init__(self, schedule_obj):
        self.schedule = schedule_obj
        self.open_set = []
        self.closed_set = set()
        self.nodes_expanded = 0
        self.node_counter = 0  # Add counter for tie-breaking
    
    def find_path(self):
        """A* search for optimal schedule"""
        print("Starting A* search...")
        
        # Create initial node
        start_node = self.schedule.copy()
        start_node.calculate_fitness()
        
        # Priority queue: (f_score, counter, g_score, node)
        # Counter ensures we can compare when f_score is equal
        self.node_counter = 0
        heapq.heappush(self.open_set, 
                      (self.f_score(start_node), self.node_counter, 0, start_node))
        self.node_counter += 1
        
        while self.open_set:
            f_score, _, g_score, current = heapq.heappop(self.open_set)
            self.nodes_expanded += 1
            
            # Progress
            if self.nodes_expanded % 100 == 0:
                print(f"\rA*: Nodes expanded: {self.nodes_expanded}, Queue: {len(self.open_set)}", end="")
            
            # Check if goal reached
            if self.is_goal(current):
                print(f"\n✅ A* found solution after {self.nodes_expanded} nodes")
                print(f"   Fitness: {current.fitness:.2f}")
                return current
            
            # Generate successors
            for successor, successor_g in self.generate_successors(current, g_score):
                if self.get_state_id(successor) in self.closed_set:
                    continue
                
                successor_f = self.f_score(successor)
                
                # Check if already in open set with better g
                found_better = False
                for i, (f, cnt, g, node) in enumerate(self.open_set):
                    if self.get_state_id(node) == self.get_state_id(successor):
                        if g <= successor_g:
                            found_better = True
                            break
                        # Remove old entry
                        self.open_set[i] = self.open_set[-1]
                        self.open_set.pop()
                        heapq.heapify(self.open_set)
                        break
                
                if not found_better:
                    heapq.heappush(self.open_set, 
                                  (successor_f, self.node_counter, successor_g, successor))
                    self.node_counter += 1
            
            self.closed_set.add(self.get_state_id(current))
        
        print(f"\n❌ A* could not find solution")
        return None
    
    def f_score(self, schedule_obj):
        """f(n) = g(n) + h(n)"""
        g = self.g_score(schedule_obj)
        h = self.heuristic(schedule_obj)
        return g + h
    
    def g_score(self, schedule_obj):
        """Actual cost from start"""
        # Number of unscheduled courses (inverse)
        unscheduled = sum(1 for c in schedule_obj.courses if c.assigned_time is None)
        return unscheduled * 100  # Weight
    
    def heuristic(self, schedule_obj):
        """Heuristic: estimated cost to goal"""
        h = 0
        
        # Estimate for each unscheduled course
        for course in schedule_obj.courses:
            if course.assigned_time is not None:
                continue
            
            # Count possible assignments
            possible_assignments = 0
            for room in schedule_obj.rooms:
                if not room.can_accommodate(course):
                    continue
                for prof in schedule_obj.professors:
                    if not prof.can_teach(course.course_id):
                        continue
                    for day in config.DAYS:
                        for time_slot in range(len(config.TIME_SLOTS)):
                            if (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                                possible_assignments += 1
            
            # More possible assignments = lower heuristic cost
            if possible_assignments == 0:
                h += 1000  # Impossible
            else:
                h += 100 / possible_assignments
        
        return h
    
    def is_goal(self, schedule_obj):
        """Check if all courses are scheduled"""
        return all(c.assigned_time is not None for c in schedule_obj.courses)
    
    def generate_successors(self, schedule_obj, current_g):
        """Generate next possible states with their g cost"""
        successors = []
        
        # Find first unscheduled course
        unscheduled_courses = [c for c in schedule_obj.courses if c.assigned_time is None]
        if not unscheduled_courses:
            return successors
        
        # Use MRV (Minimum Remaining Values) heuristic
        next_course = None
        min_options = float('inf')
        
        for course in unscheduled_courses:
            # Count options for this course
            options = 0
            for room in schedule_obj.rooms:
                if not room.can_accommodate(course):
                    continue
                for prof in schedule_obj.professors:
                    if not prof.can_teach(course.course_id):
                        continue
                    for day in config.DAYS:
                        for time_slot in range(len(config.TIME_SLOTS)):
                            if (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                                options += 1
            
            if options < min_options:
                min_options = options
                next_course = course
        
        if not next_course:
            return successors
        
        # Generate all possible assignments for this course
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
                        
                        # Create new schedule
                        successor = schedule_obj.copy()
                        
                        # Find objects in the copied schedule
                        course_copy = next((c for c in successor.courses 
                                          if c.course_id == next_course.course_id), None)
                        room_copy = next((r for r in successor.rooms 
                                        if r.room_id == room.room_id), None)
                        prof_copy = next((p for p in successor.professors 
                                        if p.professor_id == prof.professor_id), None)
                        
                        if course_copy and room_copy and prof_copy:
                            successor.add_assignment(course_copy, room_copy, prof_copy, 
                                                   day, time_slot)
                            
                            # Calculate g cost (current_g + cost of this assignment)
                            assignment_cost = 1  # Each assignment costs 1
                            successors.append((successor, current_g + assignment_cost))
        
        return successors
    
    def get_state_id(self, schedule_obj):
        """Create unique ID for a schedule state"""
        assignments = []
        for course in schedule_obj.courses:
            if course.assigned_time is not None:
                assignments.append(f"{course.course_id}:{course.assigned_day}:{course.assigned_time}")
        assignments.sort()
        return "|".join(assignments)