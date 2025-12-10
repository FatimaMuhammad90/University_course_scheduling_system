from collections import deque
import config


def bfs(initial_schedule, max_depth=None):
    if max_depth is None:
        max_depth = 5  
    
    print("\n[BFS Algorithm Starting]")
    print(f"  Courses to schedule: {len(initial_schedule.courses)}")
    print(f"  Max search depth: {max_depth}")
    
    initial_state = initial_schedule.copy()
    
    # schedule, depth
    queue = deque()
    queue.append((initial_state, 0))
    
    visited = set()
    nodes_expanded = 0
    max_queue_size = 0
    
    while queue and nodes_expanded < 10000:
        current_schedule, depth = queue.popleft()
        nodes_expanded += 1
        
        if nodes_expanded % 100 == 0:
            print(f"\r  Explored {nodes_expanded} states, queue: {len(queue)}", end="")
        
        # check karey if current schedule is complete and valid
        if is_schedule_complete(current_schedule):
            if current_schedule.is_valid():
                print(f"\n\n[SUCCESS] Found valid schedule!")
                print(f"  Nodes expanded: {nodes_expanded}")
                print(f"  Search depth: {depth}")
                print(f"  Courses scheduled: {len(current_schedule.assignments)}/{len(current_schedule.courses)}")
                return current_schedule
        
        if depth >= max_depth:
            continue
        
        # Find unscheduled courses
        scheduled_course_ids = get_scheduled_course_ids(current_schedule)
        unscheduled_courses = [
            course for course in current_schedule.courses 
            if course.course_id not in scheduled_course_ids
        ]
        
        if not unscheduled_courses:
            continue
        
        next_course = unscheduled_courses[0]
    
        for room in current_schedule.rooms:
            if not room.can_accommodate(next_course):
                continue
            
            for professor in current_schedule.professors:
                if not professor.can_teach(next_course.course_id):
                    continue
                
                for day in config.DAYS:
                    for time_slot in range(len(config.TIME_SLOTS)):
                        # Check availability
                        if not (room.is_available(day, time_slot) and 
                                professor.is_available(day, time_slot)):
                            continue
                        
                        # Create new schedule with this assignment
                        new_schedule = current_schedule.copy()
                        
                        # Find corresponding objects in the copy
                        new_course = find_course(new_schedule, next_course.course_id)
                        new_room = find_room(new_schedule, room.room_id)
                        new_prof = find_professor(new_schedule, professor.professor_id)
                        
                        if not (new_course and new_room and new_prof):
                            continue
                        
                        # Make the assignment
                        success = new_schedule.add_assignment(
                            new_course, new_room, new_prof, day, time_slot
                        )
                        
                        if not success:
                            continue
                        
                        # Create state ID and check for duplicates
                        state_id = create_state_id(new_schedule)
                        if state_id in visited:
                            continue
                        
                        visited.add(state_id)
                        queue.append((new_schedule, depth + 1))
                        
                        # Track max queue size
                        if len(queue) > max_queue_size:
                            max_queue_size = len(queue)
    
    print(f"\n\n[FAILED] No valid schedule found")
    print(f"  Total nodes expanded: {nodes_expanded}")
    print(f"  Maximum queue size: {max_queue_size}")
    print(f"  Visited states: {len(visited)}")
    
    return None


def is_schedule_complete(schedule_obj):
    """Check if all courses are scheduled"""
    if not hasattr(schedule_obj, 'assignments'):
        return False
    
    scheduled_course_ids = get_scheduled_course_ids(schedule_obj)
    all_course_ids = {course.course_id for course in schedule_obj.courses}
    
    return scheduled_course_ids == all_course_ids


def get_scheduled_course_ids(schedule_obj):
    """Extract course IDs from assignments (handles both dict and object formats)"""
    scheduled_ids = set()
    
    if not hasattr(schedule_obj, 'assignments'):
        return scheduled_ids
    
    for assignment in schedule_obj.assignments:
        if isinstance(assignment, dict):
            # Dictionary format
            if 'course_id' in assignment:
                scheduled_ids.add(assignment['course_id'])
            elif 'course' in assignment and hasattr(assignment['course'], 'course_id'):
                scheduled_ids.add(assignment['course'].course_id)
        else:
            # Object format
            if hasattr(assignment, 'course') and hasattr(assignment.course, 'course_id'):
                scheduled_ids.add(assignment.course.course_id)
            elif hasattr(assignment, 'course_id'):
                scheduled_ids.add(assignment.course_id)
    
    return scheduled_ids


def create_state_id(schedule_obj):
    """Create a unique ID for a schedule state"""
    if not hasattr(schedule_obj, 'assignments') or not schedule_obj.assignments:
        return "empty"
    
    parts = []
    
    for assignment in schedule_obj.assignments:
        if isinstance(assignment, dict):
            # Dictionary format
            course_id = assignment.get('course_id', '')
            day = assignment.get('day', '')
            time_slot = assignment.get('time_slot', '')
            room_id = assignment.get('room_id', '')
            prof_id = assignment.get('professor_id', '')
        else:
            # Object format
            if hasattr(assignment, 'course') and hasattr(assignment.course, 'course_id'):
                course_id = assignment.course.course_id
            else:
                course_id = getattr(assignment, 'course_id', '')
            
            day = getattr(assignment, 'day', '')
            time_slot = getattr(assignment, 'time_slot', '')
            
            if hasattr(assignment, 'room') and hasattr(assignment.room, 'room_id'):
                room_id = assignment.room.room_id
            else:
                room_id = getattr(assignment, 'room_id', '')
            
            if hasattr(assignment, 'professor') and hasattr(assignment.professor, 'professor_id'):
                prof_id = assignment.professor.professor_id
            else:
                prof_id = getattr(assignment, 'professor_id', '')
        
        parts.append(f"{course_id}:{day}:{time_slot}:{room_id}:{prof_id}")
    
    # Sort for consistent ordering
    parts.sort()
    return "|".join(parts)


def find_course(schedule_obj, course_id):
    """Find a course by ID in the schedule"""
    for course in schedule_obj.courses:
        if course.course_id == course_id:
            return course
    return None


def find_room(schedule_obj, room_id):
    """Find a room by ID in the schedule"""
    for room in schedule_obj.rooms:
        if room.room_id == room_id:
            return room
    return None


def find_professor(schedule_obj, professor_id):
    """Find a professor by ID in the schedule"""
    for professor in schedule_obj.professors:
        if professor.professor_id == professor_id:
            return professor
    return None
