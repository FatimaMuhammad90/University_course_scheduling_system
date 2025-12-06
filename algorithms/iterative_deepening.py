# algorithms/iterative_deepening.py - UPDATED VERSION
"""
Iterative Deepening Depth-First Search for course scheduling
"""

import config
from models import schedule

def iterative_deepening(initial_schedule, max_depth=None):
    """
    Iterative Deepening Depth-First Search
    
    Combines benefits of BFS (completeness) and DFS (memory efficiency)
    by repeatedly running depth-limited search with increasing depth limits.
    
    Args:
        initial_schedule: Starting schedule object
        max_depth: Maximum depth to search (uses config if None)
    
    Returns:
        schedule object if solution found, None otherwise
    """
    
    # Get parameters from config or use defaults
    if max_depth is None:
        try:
            max_depth = config.ALGORITHM_CONFIG['iterative_deepening']['max_depth']
        except (ImportError, KeyError):
            max_depth = 5
    
    try:
        depth_increment = config.ALGORITHM_CONFIG['iterative_deepening']['depth_increment']
    except (ImportError, KeyError):
        depth_increment = 1
    
    print(f"Starting Iterative Deepening (max_depth={max_depth})...")
    
    # Try increasing depth limits
    for depth in range(1, max_depth + 1, depth_increment):
        print(f"\nTrying depth limit: {depth}")
        
        # Run depth-limited search
        result = depth_limited_search(initial_schedule, depth)
        if result:
            print(f"Found solution at depth {depth}")
            print(f"   Fitness: {result.calculate_fitness():.2f}")
            return result
    
    print(" Iterative Deepening could not find solution within depth limit")
    return None

def depth_limited_search(initial_schedule, depth_limit):
    """
    Depth-limited search (DFS with depth limit)
    
    Args:
        initial_schedule: Starting schedule
        depth_limit: Maximum search depth
    
    Returns:
        schedule object if solution found, None otherwise
    """
    
    visited = set()
    nodes_expanded = 0
    
    def dls_recursive(current_sched, depth, path):
        nonlocal nodes_expanded
        nodes_expanded += 1
        
        if nodes_expanded % 100 == 0:
            print(f"\rDLS Depth {depth_limit}: Depth {depth}, Nodes: {nodes_expanded}", end="")
        
        # Check if complete
        if len(path) == len(current_sched.courses):
            if current_sched.is_valid():
                return current_sched
        
        # Depth limit reached
        if depth >= depth_limit:
            return None
        
        # Find next course to schedule (MRV heuristic)
        next_course = None
        min_options = float('inf')
        
        for course in current_sched.courses:
            if course.assigned_time is not None:
                continue
            
            # Count possible assignments for this course
            options = count_possible_assignments(course, current_sched)
            if options < min_options and options > 0:
                min_options = options
                next_course = course
        
        if not next_course:
            return None
        
        # Get days and time slots
        try:
            from config import DAYS, TIME_SLOTS
            days = DAYS
            time_slots = TIME_SLOTS
        except ImportError:
            days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
            time_slots = ["8:00-9:30", "9:30-11:00", "11:00-12:30", 
                         "13:00-14:30", "14:30-16:00", "16:00-17:30"]
        
        # Generate all possible assignments
        assignments = []
        for room in current_sched.rooms:
            if not room.can_accommodate(next_course):
                continue
            
            for prof in current_sched.professors:
                if not prof.can_teach(next_course.course_id):
                    continue
                
                for day in days:
                    for time_slot in range(len(time_slots)):
                        if not (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                            continue
                        
                        # Calculate preference score for ordering
                        score = 0
                        time_of_day = "morning" if time_slot <= 2 else "afternoon"
                        if hasattr(next_course, 'preferred_times') and time_of_day in next_course.preferred_times:
                            score += 2
                        
                        if hasattr(prof, 'get_preference_score'):
                            try:
                                score += prof.get_preference_score(day, time_slot)
                            except:
                                pass
                        
                        assignments.append((room, prof, day, time_slot, score))
        
        # Order by preference (highest first)
        assignments.sort(key=lambda x: x[4], reverse=True)
        
        # Try each assignment
        for room, prof, day, time_slot, _ in assignments:
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
                
                # Create state identifier
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
                
                # Recursive call
                result = dls_recursive(new_sched, depth + 1, new_path)
                if result is not None:
                    return result
        
        return None
    
    # Start search
    result = dls_recursive(initial_schedule.copy(), 0, [])
    
    if result:
        print(f"\nDepth-limited search found solution at depth {depth_limit}")
        print(f"   Nodes expanded: {nodes_expanded}")
    else:
        print(f"\ No solution found within depth {depth_limit} ({nodes_expanded} nodes)")
    
    return result

def count_possible_assignments(course, schedule_obj):
    """Count possible assignments for a course"""
    count = 0
    
    try:
        from config import DAYS, TIME_SLOTS
        days = DAYS
        time_slots = TIME_SLOTS
    except ImportError:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        time_slots = ["8:00-9:30", "9:30-11:00", "11:00-12:30", 
                     "13:00-14:30", "14:30-16:00", "16:00-17:30"]
    
    for room in schedule_obj.rooms:
        if not room.can_accommodate(course):
            continue
        for prof in schedule_obj.professors:
            if not prof.can_teach(course.course_id):
                continue
            for day in days:
                for time_slot in range(len(time_slots)):
                    if (room.is_available(day, time_slot) and 
                        prof.is_available(day, time_slot)):
                        count += 1
    
    return count

def create_state_id(schedule_obj):
    """Create unique identifier for a schedule state"""
    assignments = []
    for course in schedule_obj.courses:
        if course.assigned_time is not None:
            assignments.append(f"{course.course_id}:{course.assigned_day}:{course.assigned_time}")
    assignments.sort()
    return "|".join(assignments)