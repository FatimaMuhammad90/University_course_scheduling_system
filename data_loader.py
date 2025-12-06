"""
Data Loader Module
Converts JSON data to model objects
"""
from models import course, room, professor

def json_to_models(json_data):
    """
    Convert JSON data to model objects
    
    Args:
        json_data: Dictionary with 'professors', 'rooms', 'courses' keys
    
    Returns:
        Dictionary with model objects
    """
    # Create professor objects
    professors = []
    for prof_data in json_data['professors']:
        prof = professor(
            professor_id=prof_data['professor_id'],
            name=prof_data['name'],
            department=prof_data['department'],
            courses=prof_data['courses'],
            max_hours=prof_data.get('max_hours', 12),
            preferences=prof_data.get('preferences', {})
        )
        professors.append(prof)
    
    # Create room objects
    rooms = []
    for room_data in json_data['rooms']:
        r = room(
            room_id=room_data['room_id'],
            name=room_data['name'],
            capacity=room_data['capacity'],
            room_type=room_data['room_type'],
            features=room_data.get('features', []),
            building=room_data['building'],
            cost_per_hour=room_data.get('cost_per_hour', 10.0)
        )
        rooms.append(r)
    
    # Create course objects
    courses = []
    for course_data in json_data['courses']:
        c = course(
            course_id=course_data['course_id'],
            name=course_data['name'],
            department=course_data['department'],
            credits=course_data.get('credits', 3),
            students=course_data['students'],
            course_type=course_data['course_type'],
            professors=course_data['professors'],
            prerequisites=course_data.get('prerequisites', []),
            preferred_times=course_data.get('preferred_times', []),
            required_rooms=course_data.get('required_rooms', [])
        )
        courses.append(c)
    
    return {
        'professors': professors,
        'rooms': rooms,
        'courses': courses
    }

def load_from_json_file(filename):
    """
    Load data from JSON file and convert to model objects
    
    Args:
        filename: Path to JSON file
    
    Returns:
        Dictionary with model objects
    """
    import json
    
    with open(filename, 'r') as f:
        json_data = json.load(f)
    
    return json_to_models(json_data)
