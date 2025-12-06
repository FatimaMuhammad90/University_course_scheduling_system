import sys
import config
from models import schedule

def create_state_id(sched):
    """Create a unique identifier for a schedule state"""
    assignments = []
    for course in sched.courses:
        if course.assigned_time is not None:
            assignments.append(f"{course.course_id}:{course.assigned_room}:{course.assigned_professor}:{course.assigned_day}:{course.assigned_time}")
    return hash(tuple(sorted(assignments)))

def dfs_schedule(initial_schedule, max_depth=None):
    """DFS for course scheduling"""
    if max_depth is None:
        max_depth = config.ALGORITHM_CONFIG['dfs']['max_depth']
    
    sys.setrecursionlimit(10000)
    print("Starting DFS...")
    
    visited = set()
    nodes_expanded = [0]
    solution = [None]
    
    def dfs_recursive(current_sched, depth, path):
        nodes_expanded[0] += 1
        
        if nodes_expanded[0] % 100 == 0:
            print(f"\rDFS: Depth {depth}, Nodes: {nodes_expanded[0]}", end="")
        
        # Check if complete
        if len(path) == len(current_sched.courses):
            if current_sched.is_valid():
                solution[0] = current_sched
                return True
        
        if depth >= max_depth or nodes_expanded[0] >= config.ALGORITHM_CONFIG['dfs']['max_nodes']:
            return False
        
        # Find next course (MRV heuristic)
        next_course = None
        min_options = float('inf')
        
        for course in current_sched.courses:
            if course.assigned_time is not None:
                continue
            
            options = 0
            for room in current_sched.rooms:
                if not room.can_accommodate(course):
                    continue
                for prof in current_sched.professors:
                    if not prof.can_teach(course.course_id):
                        continue
                    for day in config.DAYS:
                        for time in range(len(config.TIME_SLOTS)):
                            if (room.is_available(day, time) and 
                                prof.is_available(day, time)):
                                options += 1
            
            if options < min_options and options > 0:
                min_options = options
                next_course = course
        
        if not next_course:
            return False
        
        # Generate and try assignments (order by preference)
        assignments = []
        for room in current_sched.rooms:
            if not room.can_accommodate(next_course):
                continue
            
            for prof in current_sched.professors:
                if not prof.can_teach(next_course.course_id):
                    continue
                
                for day in config.DAYS:
                    for time_slot in range(len(config.TIME_SLOTS)):
                        if not (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                            continue
                        
                        # Calculate preference score
                        score = 0
                        time_of_day = "morning" if time_slot <= 2 else "afternoon"
                        if time_of_day in next_course.preferred_times:
                            score += 2
                        score += prof.get_preference_score(day, time_slot)
                        
                        assignments.append((room, prof, day, time_slot, score))
        
        # Sort by preference score (highest first)
        assignments.sort(key=lambda x: x[4], reverse=True)
        
        for room, prof, day, time_slot, _ in assignments:
            new_sched = current_sched.copy()
            
            new_course = next((c for c in new_sched.courses 
                             if c.course_id == next_course.course_id), None)
            new_room = next((r for r in new_sched.rooms 
                           if r.room_id == room.room_id), None)
            new_prof = next((p for p in new_sched.professors 
                           if p.professor_id == prof.professor_id), None)
            
            if new_course and new_room and new_prof:
                new_sched.add_assignment(new_course, new_room, new_prof, 
                                       day, time_slot)
                
                state_id = create_state_id(new_sched)
                if state_id in visited:
                    continue
                visited.add(state_id)
                
                new_path = path + [{
                    'course': new_course.course_id,
                    'room': new_room.room_id,
                    'prof': new_prof.professor_id,
                    'day': day,
                    'time': time_slot
                }]
                
                if dfs_recursive(new_sched, depth + 1, new_path):
                    return True
        
        return False
    
    # Start DFS
    if dfs_recursive(initial_schedule.copy(), 0, []):
        print(f"\nDFS found solution")
        print(f"   Nodes: {nodes_expanded[0]}, Fitness: {solution[0].calculate_fitness():.2f}")
        return solution[0]
    else:
        print(f"\n❌ DFS exhausted search ({nodes_expanded[0]} nodes)")
        return None