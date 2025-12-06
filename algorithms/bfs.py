from collections import deque
import config
from models import schedule

def bfs_schedule(initial_schedule, max_depth=None):
    """BFS for course scheduling"""
    if max_depth is None:
        max_depth = config.ALGORITHM_CONFIG['bfs']['max_depth']
    
    print("Starting BFS...")
    
    # Queue: (schedule, depth, path)
    queue = deque()
    queue.append((initial_schedule.copy(), 0, []))
    
    visited = set()
    nodes_expanded = 0
    
    while queue and nodes_expanded < config.ALGORITHM_CONFIG['bfs']['max_nodes']:
        current_sched, depth, path = queue.popleft()
        nodes_expanded += 1
        
        if nodes_expanded % 100 == 0:
            print(f"\rBFS: Depth {depth}, Queue: {len(queue)}, Nodes: {nodes_expanded}", end="")
        
        # Check if complete
        if len(path) == len(current_sched.courses):
            if current_sched.is_valid():
                print(f"\n BFS found solution at depth {depth}")
                print(f"   Nodes: {nodes_expanded}, Fitness: {current_sched.calculate_fitness():.2f}")
                return current_sched
        
        if depth >= max_depth:
            continue
        
        # Find next course to schedule (MRV)
        next_course = None
        min_options = float('inf')
        
        for course in current_sched.courses:
            if course.assigned_time is not None:
                continue
            
            # Count options for this course
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
            
            if options < min_options:
                min_options = options
                next_course = course
        
        if not next_course:
            continue
        
        # Generate all possible assignments for next course
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
                        
                        new_sched = current_sched.copy()
                        
                        # Find objects in copied schedule
                        new_course = next((c for c in new_sched.courses 
                                         if c.course_id == next_course.course_id), None)
                        new_room = next((r for r in new_sched.rooms 
                                       if r.room_id == room.room_id), None)
                        new_prof = next((p for p in new_sched.professors 
                                       if p.professor_id == prof.professor_id), None)
                        
                        if new_course and new_room and new_prof:
                            new_sched.add_assignment(new_course, new_room, new_prof, 
                                                   day, time_slot)
                            
                            # Create state ID
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
                            
                            queue.append((new_sched, depth + 1, new_path))
    
    print(f"\n BFS exhausted search ({nodes_expanded} nodes)")
    return None

def create_state_id(schedule_obj):
    assignments = []
    for course in schedule_obj.courses:
        if course.assigned_time is not None:
            assignments.append(f"{course.course_id}:{course.assigned_day}:{course.assigned_time}")
    assignments.sort()
    return "|".join(assignments)