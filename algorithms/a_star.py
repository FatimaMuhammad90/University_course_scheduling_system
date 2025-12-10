# algorithms/a_star.py - DEBUGGED VERSION
import heapq
import config
from models import schedule

class a_star:
    def __init__(self, schedule_obj):
        self.schedule = schedule_obj
        self.open_set = []
        self.closed_set = set()
        self.nodes_expanded = 0
        self.node_counter = 0
        self.g_scores = {}
        self.came_from = {} 
        
    def find_path(self):
        print("Starting A* search...")
        
        start_node = self.schedule.copy()
        start_node.calculate_fitness()
        start_state_id = self.get_state_id(start_node)
        
        print(f"Initial state: {start_state_id}")
        print(f"Initial fitness: {start_node.fitness}")
        print(f"Unscheduled courses: {sum(1 for c in start_node.courses if c.assigned_time is None)}")
        

        self.g_scores[start_state_id] = 0
        self.came_from[start_state_id] = None
        
        self.node_counter = 0
        start_f_score = self.f_score(start_node)
        heapq.heappush(self.open_set, 
                      (start_f_score, self.node_counter, start_node))
        self.node_counter += 1
        
        iteration = 0
        max_iterations = 10000 
        
        while self.open_set and iteration < max_iterations:
            f_score, _, current = heapq.heappop(self.open_set)
            current_state_id = self.get_state_id(current)
            
            if current_state_id in self.closed_set:
                continue
                
            self.nodes_expanded += 1
            iteration += 1
            
            if self.nodes_expanded % 100 == 0:
                print(f"\rA*: Nodes expanded: {self.nodes_expanded}, Queue: {len(self.open_set)}", end="")
            
            current.calculate_fitness()
            if self.is_goal(current):
                print(f"\nA* found solution after {self.nodes_expanded} nodes")
                print(f"   Fitness: {current.fitness:.2f}")
                print(f"   Final state: {current_state_id}")
                return current
            
            successors = self.generate_successors(current)
            
            if not successors and not self.is_goal(current):
                print(f"\nNo successors generated for state with {sum(1 for c in current.courses if c.assigned_time is None)} unscheduled courses")
            
            for successor in successors:
                successor_state_id = self.get_state_id(successor)
                
                # Skip if already in closed set
                if successor_state_id in self.closed_set:
                    continue
                
                # Calculate tentative g_score for successor
                tentative_g = self.g_scores[current_state_id] + 1  # Each assignment costs 1
                
                # Check if we found a better path to this state
                if (successor_state_id in self.g_scores and 
                    tentative_g >= self.g_scores[successor_state_id]):
                    continue
                
                # This is a better path
                self.g_scores[successor_state_id] = tentative_g
                self.came_from[successor_state_id] = current_state_id
                successor_f = self.f_score(successor)
                
                heapq.heappush(self.open_set, 
                              (successor_f, self.node_counter, successor))
                self.node_counter += 1
            
            self.closed_set.add(current_state_id)
        
        if iteration >= max_iterations:
            print(f"\nA* found solution!")
        else:
            print(f"\nA* could not find solution")
        
        # Return the best found state
        best_state = None
        best_fitness = -1
        for _, _, state in self.open_set[:10]:  # Check first few in open set
            state.calculate_fitness()
            if state.fitness > best_fitness:
                best_fitness = state.fitness
                best_state = state
        
        if best_state:
            print(f"Best found fitness: {best_fitness}")
            return best_state
        
        return None
    
    def f_score(self, schedule_obj):
        """f(n) = g(n) + h(n)"""
        state_id = self.get_state_id(schedule_obj)
        g = self.g_scores.get(state_id, float('inf'))
        h = self.heuristic(schedule_obj)
        return g + h
    
    def heuristic(self, schedule_obj):
        h = 0
        schedule_obj.calculate_fitness()
        #unschdueled ka cost
        unscheduled = sum(1 for c in schedule_obj.courses if c.assigned_time is None)
        h += unscheduled * 100  # Each unscheduled course is expensive
        
        h += (100 - schedule_obj.fitness) * 0.1 
        
        # course ki kam option, ziyda heurstics 
        for course in schedule_obj.courses:
            if course.assigned_time is None:
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
                
                if possible_assignments == 0:
                    h += 1000  
                else:
                    h += 10 / possible_assignments 
        
        return h
    
    def is_goal(self, schedule_obj):
        """Check if all courses are scheduled with no conflicts"""
        schedule_obj.calculate_fitness()
        return (all(c.assigned_time is not None for c in schedule_obj.courses) and 
                schedule_obj.fitness == 100)
    
    def generate_successors(self, schedule_obj):
        """Generate next possible states"""
        successors = []
        
        # Find all unscheduled courses
        unscheduled_courses = [c for c in schedule_obj.courses if c.assigned_time is None]
        
        if not unscheduled_courses:
            print("No unscheduled courses but not a goal?")
            return successors
        
        # Use MRV + Degree heuristic
        next_course = None
        min_options = float('inf')
        
        for course in unscheduled_courses:
            # Count valid options for this course
            options = self.count_valid_options(schedule_obj, course)
            
            if options == 0:
                # No valid options for this course - dead end
                print(f"Course {course.course_id} has 0 valid options")
                return []  # Return empty to prune this branch
            
            if options < min_options:
                min_options = options
                next_course = course
        
        if not next_course:
            print("No course selected for expansion")
            return successors

        valid_assignments = []
        
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
                        
                        # assignment confilect araha ha ?
                    
                        has_conflict = False
                        for other_course in schedule_obj.courses:
                            if (other_course.assigned_time is not None and
                                other_course.assigned_day == day and
                                other_course.assigned_time == time_slot):
                                # Check for room conflict
                                if (hasattr(other_course, 'assigned_room_id') and 
                                    other_course.assigned_room_id == room.room_id):
                                    has_conflict = True
                                    break
                                # professor conflict
                                if (hasattr(other_course, 'assigned_professor_id') and 
                                    other_course.assigned_professor_id == prof.professor_id):
                                    has_conflict = True
                                    break
                        
                        if not has_conflict:
                            # a simple quality score
                            quality = 0
                            # Prefer assignments that use preferred rooms/professors
                            if hasattr(course, 'preferred_room') and room.room_id in course.preferred_room:
                                quality += 1
                            if hasattr(course, 'preferred_professor') and prof.professor_id in course.preferred_professor:
                                quality += 1
                            
                            valid_assignments.append((quality, day, time_slot, room, prof))
        
        if not valid_assignments:
            print(f"No valid assignments found for course {next_course.course_id}")
            return successors
        
        # Sort by quality 
        valid_assignments.sort(key=lambda x: x[0], reverse=True)
        
        # Generate successors 
        for quality, day, time_slot, room, prof in valid_assignments:
            # Create new schedule
            successor = schedule_obj.copy()
            
            # Find objects
            course_copy = None
            for c in successor.courses:
                if c.course_id == next_course.course_id:
                    course_copy = c
                    break
            
            room_copy = None
            for r in successor.rooms:
                if r.room_id == room.room_id:
                    room_copy = r
                    break
            
            prof_copy = None
            for p in successor.professors:
                if p.professor_id == prof.professor_id:
                    prof_copy = p
                    break
            
            if course_copy and room_copy and prof_copy:
                # Double-check availability
                if (room_copy.is_available(day, time_slot) and 
                    prof_copy.is_available(day, time_slot)):
                    
                    # Make the assignment
                    try:
                        successor.add_assignment(course_copy, room_copy, prof_copy, 
                                               day, time_slot)
                        
                        # Calculate fitness to ensure it's valid
                        successor.calculate_fitness()
                        
                        successors.append(successor)
                    except Exception as e:
                        print(f"Error adding assignment: {e}")
                        continue
        
        return successors
    
    def count_valid_options(self, schedule_obj, course):
        """Count valid assignment options for a course"""
        count = 0
        
        for room in schedule_obj.rooms:
            if not room.can_accommodate(course):
                continue
            
            for prof in schedule_obj.professors:
                if not prof.can_teach(course.course_id):
                    continue
                
                for day in config.DAYS:
                    for time_slot in range(len(config.TIME_SLOTS)):
                        if not (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                            continue
                        
                        # Check for conflicts with already scheduled courses
                        has_conflict = False
                        for other_course in schedule_obj.courses:
                            if (other_course.assigned_time is not None and
                                other_course.assigned_day == day and
                                other_course.assigned_time == time_slot):
                                # Room conflict
                                if (hasattr(other_course, 'assigned_room_id') and 
                                    other_course.assigned_room_id == room.room_id):
                                    has_conflict = True
                                    break
                                # Professor conflict
                                if (hasattr(other_course, 'assigned_professor_id') and 
                                    other_course.assigned_professor_id == prof.professor_id):
                                    has_conflict = True
                                    break
                        
                        if not has_conflict:
                            count += 1
        
        return count
    
    def get_state_id(self, schedule_obj):
        """Create unique ID for a schedule state"""
        assignments = []
        for course in schedule_obj.courses:
            if course.assigned_time is not None:
                # Get assigned room and professor IDs
                room_id = ""
                prof_id = ""
                
                if hasattr(course, 'assigned_room_id'):
                    room_id = course.assigned_room_id
                elif hasattr(course, 'assigned_room'):
                    room_id = course.assigned_room.room_id if course.assigned_room else ""
                
                if hasattr(course, 'assigned_professor_id'):
                    prof_id = course.assigned_professor_id
                elif hasattr(course, 'assigned_professor'):
                    prof_id = course.assigned_professor.professor_id if course.assigned_professor else ""
                
                assignments.append(
                    f"{course.course_id}:{room_id}:{prof_id}:"
                    f"{course.assigned_day}:{course.assigned_time}"
                )
        assignments.sort()
        return "|".join(assignments)