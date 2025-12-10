"""
Interactive Data Collection Module with Input Validation
Collects course, professor, and room data from user and saves to JSON
"""
import json
import os

def get_valid_input(prompt, validation_func, error_message):
    """
    Get input from user with validation
    
    Args:
        prompt: The prompt to display
        validation_func: Function that returns True if input is valid
        error_message: Message to show on invalid input
    
    Returns:
        Valid user input
    """
    while True:
        user_input = input(prompt).strip()
        if validation_func(user_input):
            return user_input
        print(f" {error_message}")

def get_positive_int(prompt, default=None):
    """Get a positive integer from user"""
    while True:
        user_input = input(prompt).strip()
        
        # Handle default
        if not user_input and default is not None:
            return default
        
        try:
            value = int(user_input)
            if value > 0:
                return value
            print(f"Please enter a positive number (greater than 0)")
        except ValueError:
            print(f"Please enter a valid number")

def get_positive_float(prompt, default=None):
    """Get a positive float from user"""
    while True:
        user_input = input(prompt).strip()
        
        # Handle default
        if not user_input and default is not None:
            return default
        
        try:
            value = float(user_input)
            if value > 0:
                return value
            print(f"Please enter a positive number (greater than 0)")
        except ValueError:
            print(f"Please enter a valid number")

def get_non_empty_string(prompt):
    """Get a non-empty string from user"""
    return get_valid_input(
        prompt,
        lambda x: len(x) > 0,
        "This field cannot be empty. Please enter a value."
    )

def get_comma_separated_list(prompt, allow_empty=False):
    """Get a comma-separated list from user"""
    while True:
        user_input = input(prompt).strip()
        
        if not user_input:
            if allow_empty:
                return []
            print(f"Please enter at least one value")
            continue
        
        # Split and clean
        items = [item.strip() for item in user_input.split(",")]
        items = [item for item in items if item]  # Remove empty strings
        
        if items or allow_empty:
            return items
        print(f"Please enter at least one valid value")

def get_valid_days():
    """Get valid day names"""
    valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    
    while True:
        days_input = input("Preferred days (comma-separated, e.g., monday,wednesday): ").strip()
        
        if not days_input:
            print(f"  ✗ Please enter at least one day")
            continue
        
        days = [d.strip().lower() for d in days_input.split(",")]
        
        # Validate all days
        invalid_days = [d for d in days if d not in valid_days]
        if invalid_days:
            print(f"  ✗ Invalid days: {', '.join(invalid_days)}")
            print(f"     Valid days: {', '.join(valid_days)}")
            continue
        
        return days

def get_valid_times():
    """Get valid time preferences"""
    valid_times = ["morning", "afternoon", "evening"]
    
    while True:
        times_input = input("Preferred times (comma-separated, e.g., morning,afternoon): ").strip()
        
        if not times_input:
            print(f"Please enter at least one time preference")
            continue
        
        times = [t.strip().lower() for t in times_input.split(",")]
        
        # Validate all times
        invalid_times = [t for t in times if t not in valid_times]
        if invalid_times:
            print(f" Invalid times: {', '.join(invalid_times)}")
            print(f"  Valid times: {', '.join(valid_times)}")
            continue
        
        return times

def collect_professors():
    """Collect professor information from user with validation"""
    professors = []
    print("\n" + "=" * 70)
    print("PROFESSOR DATA COLLECTION")
    print("=" * 70)
    
    num_professors = get_positive_int("\nHow many professors do you want to add? ")
    
    professor_ids = []  # Track IDs to prevent duplicates
    
    for i in range(num_professors):
        print(f"\n--- Professor {i+1}/{num_professors} ---")
        
        # Get unique professor ID
        while True:
            prof_id = get_non_empty_string("Professor ID (e.g., prof001): ")
            if prof_id not in professor_ids:
                professor_ids.append(prof_id)
                break
            print(f" Professor ID '{prof_id}' already exists. Please use a unique ID.")
        
        prof_data = {
            "professor_id": prof_id,
            "name": get_non_empty_string("Professor Name: "),
            "department": get_non_empty_string("Department: "),
            "courses": get_comma_separated_list("Course IDs they can teach (comma-separated): "),
            "max_hours": get_positive_int("Maximum hours per week (default 12): ", default=12),
            "preferences": {
                "preferred_days": get_valid_days(),
                "preferred_times": get_valid_times()
            }
        }
        
        professors.append(prof_data)
        print(f" Added professor: {prof_data['name']}")
    
    return professors

def collect_rooms():
    """Collect room information from user with validation"""
    rooms = []
    print("\n" + "=" * 70)
    print("ROOM DATA COLLECTION")
    print("=" * 70)
    
    num_rooms = get_positive_int("\nHow many rooms do you want to add? ")
    
    room_ids = []  # Track IDs to prevent duplicates
    
    for i in range(num_rooms):
        print(f"\n--- Room {i+1}/{num_rooms} ---")
        
        # Get unique room ID
        while True:
            room_id = get_non_empty_string("Room ID (e.g., room101): ")
            if room_id not in room_ids:
                room_ids.append(room_id)
                break
            print(f"  ✗ Room ID '{room_id}' already exists. Please use a unique ID.")
        
        room_data = {
            "room_id": room_id,
            "name": get_non_empty_string("Room Name: "),
            "capacity": get_positive_int("Capacity (number of students): "),
            "room_type": get_non_empty_string("Room Type (e.g., lecture_hall, lab): "),
            "features": get_comma_separated_list("Features (comma-separated, e.g., projector,whiteboard): "),
            "building": get_non_empty_string("Building Name: "),
            "cost_per_hour": get_positive_float("Cost per hour (default 10.0): ", default=10.0)
        }
        
        rooms.append(room_data)
        print(f" Added room: {room_data['name']}")
    
    return rooms

def collect_courses():
    """Collect course information from user with validation"""
    courses = []
    print("\n" + "=" * 70)
    print("COURSE DATA COLLECTION")
    print("=" * 70)
    
    num_courses = get_positive_int("\nHow many courses do you want to add? ")
    
    course_ids = []  
    
    for i in range(num_courses):
        print(f"\n--- Course {i+1}/{num_courses} ---")
        
        # Get unique course ID
        while True:
            course_id = get_non_empty_string("Course ID (e.g., cs101): ")
            if course_id not in course_ids:
                course_ids.append(course_id)
                break
            print(f"  ✗ Course ID '{course_id}' already exists. Please use a unique ID.")
        
        course_data = {
            "course_id": course_id,
            "name": get_non_empty_string("Course Name: "),
            "department": get_non_empty_string("Department: "),
            "credits": get_positive_int("Credits (default 3): ", default=3),
            "students": get_positive_int("Number of students enrolled: "),
            "course_type": get_non_empty_string("Course Type (e.g., lecture, lab): "),
            "professors": get_comma_separated_list("Professor IDs who can teach (comma-separated): "),
            "preferred_times": get_comma_separated_list("Preferred times (comma-separated, e.g., morning,afternoon): ", allow_empty=True),
            "required_rooms": get_comma_separated_list("Required room features (comma-separated, e.g., projector,computers): ", allow_empty=True)
        }
        
        # Optional prerequisites
        course_data["prerequisites"] = get_comma_separated_list(
            "Prerequisites (comma-separated course IDs, or press Enter for none): ",
            allow_empty=True
        )
        
        courses.append(course_data)
        print(f"Added course: {course_data['name']}")
    
    return courses

def save_data_to_json(professors, rooms, courses, filename="data/schedule_data.json"):
    """Save collected data to JSON file"""
    os.makedirs("data", exist_ok=True)
    
    data = {
        "professors": professors,
        "rooms": rooms,
        "courses": courses
    }
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\n Data saved to {filename}")
    return filename

def load_data_from_json(filename="data/schedule_data.json"):
    """Load data from JSON file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Data file {filename} not found")
    
    with open(filename, "r") as f:
        data = json.load(f)
    
    return data

def interactive_data_collection():
    """Main interactive data collection flow with validation"""
    print("\n" + "=" * 70)
    print("UNIVERSITY COURSE SCHEDULING - DATA COLLECTION")
    print("=" * 70)
    print("\nThis wizard will help you input all the required data.")
    print("You can also load data from an existing JSON file.\n")
    
    # Get choice with validation
    while True:
        choice = input("Do you want to (1) Enter new data or (2) Load from file? [1/2]: ").strip()
        if choice in ['1', '2']:
            break
        print("Please enter 1 or 2")
    
    if choice == "2":
        while True:
        
            filename = "university_data.json"
            
        
            data = load_data_from_json(filename)
            print(f"\n Loaded data from {filename}")
            print(f"    Professors: {len(data['professors'])}")
            print(f"    Rooms: {len(data['rooms'])}")
            print(f"    Courses: {len(data['courses'])}")
            return data

    
    if choice == "1":
        # Collect data with validation
        professors = collect_professors()
        rooms = collect_rooms()
        courses = collect_courses()
        
        # Save to JSON
        print("\n" + "=" * 70)
        print("SAVING DATA")
        print("=" * 70)
        
        while True:
            save_choice = input("\nDo you want to save this data? [y/n]: ").strip().lower()
            if save_choice in ['y', 'n']:
                break
            print("Please enter 'y' or 'n'")
        
        if save_choice == 'y':
            filename = "data/university_data.json"
            save_data_to_json(professors, rooms, courses, filename)
        
        return {
            "professors": professors,
            "rooms": rooms,
            "courses": courses
        }
    
    return None

if __name__ == "__main__":
    # Test the data collection
    data = interactive_data_collection()
    if data:
        print("\n" + "=" * 70)
        print("DATA COLLECTION COMPLETE")
        print("=" * 70)
        print(f"\nCollected:")
        print(f"  {len(data['professors'])} professors")
        print(f"  {len(data['rooms'])} rooms")
        print(f"  {len(data['courses'])} courses")
