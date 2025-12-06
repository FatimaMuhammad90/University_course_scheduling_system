"""
Interactive Data Collection Module
Collects course, professor, and room data from user and saves to JSON
"""
import json
import os

def collect_professors():
    """Collect professor information from user"""
    professors = []
    print("\n" + "=" * 70)
    print("PROFESSOR DATA COLLECTION")
    print("=" * 70)
    
    num_professors = int(input("\nHow many professors do you want to add? "))
    
    for i in range(num_professors):
        print(f"\n--- Professor {i+1} ---")
        prof_data = {
            "professor_id": input("Professor ID (e.g., prof001): ").strip(),
            "name": input("Professor Name: ").strip(),
            "department": input("Department: ").strip(),
            "courses": input("Course IDs they can teach (comma-separated): ").strip().split(","),
            "max_hours": int(input("Maximum hours per week (default 12): ") or "12"),
            "preferences": {
                "preferred_days": input("Preferred days (comma-separated, e.g., monday,wednesday): ").strip().split(","),
                "preferred_times": input("Preferred times (comma-separated, e.g., morning,afternoon): ").strip().split(",")
            }
        }
        # Clean up whitespace
        prof_data["courses"] = [c.strip() for c in prof_data["courses"]]
        prof_data["preferences"]["preferred_days"] = [d.strip().lower() for d in prof_data["preferences"]["preferred_days"]]
        prof_data["preferences"]["preferred_times"] = [t.strip().lower() for t in prof_data["preferences"]["preferred_times"]]
        
        professors.append(prof_data)
        print(f"✓ Added professor: {prof_data['name']}")
    
    return professors

def collect_rooms():
    """Collect room information from user"""
    rooms = []
    print("\n" + "=" * 70)
    print("ROOM DATA COLLECTION")
    print("=" * 70)
    
    num_rooms = int(input("\nHow many rooms do you want to add? "))
    
    for i in range(num_rooms):
        print(f"\n--- Room {i+1} ---")
        room_data = {
            "room_id": input("Room ID (e.g., room101): ").strip(),
            "name": input("Room Name: ").strip(),
            "capacity": int(input("Capacity (number of students): ")),
            "room_type": input("Room Type (e.g., lecture_hall, lab): ").strip(),
            "features": input("Features (comma-separated, e.g., projector,whiteboard): ").strip().split(","),
            "building": input("Building Name: ").strip(),
            "cost_per_hour": float(input("Cost per hour (default 10.0): ") or "10.0")
        }
        # Clean up whitespace
        room_data["features"] = [f.strip() for f in room_data["features"]]
        
        rooms.append(room_data)
        print(f"✓ Added room: {room_data['name']}")
    
    return rooms

def collect_courses():
    """Collect course information from user"""
    courses = []
    print("\n" + "=" * 70)
    print("COURSE DATA COLLECTION")
    print("=" * 70)
    
    num_courses = int(input("\nHow many courses do you want to add? "))
    
    for i in range(num_courses):
        print(f"\n--- Course {i+1} ---")
        course_data = {
            "course_id": input("Course ID (e.g., cs101): ").strip(),
            "name": input("Course Name: ").strip(),
            "department": input("Department: ").strip(),
            "credits": int(input("Credits (default 3): ") or "3"),
            "students": int(input("Number of students enrolled: ")),
            "course_type": input("Course Type (e.g., lecture, lab): ").strip(),
            "professors": input("Professor IDs who can teach (comma-separated): ").strip().split(","),
            "preferred_times": input("Preferred times (comma-separated, e.g., morning,afternoon): ").strip().split(","),
            "required_rooms": input("Required room features (comma-separated, e.g., projector,computers): ").strip().split(",")
        }
        
        # Optional prerequisites
        prereq_input = input("Prerequisites (comma-separated course IDs, or press Enter for none): ").strip()
        if prereq_input:
            course_data["prerequisites"] = [p.strip() for p in prereq_input.split(",")]
        else:
            course_data["prerequisites"] = []
        
        # Clean up whitespace
        course_data["professors"] = [p.strip() for p in course_data["professors"]]
        course_data["preferred_times"] = [t.strip().lower() for t in course_data["preferred_times"]]
        course_data["required_rooms"] = [r.strip() for r in course_data["required_rooms"]]
        
        courses.append(course_data)
        print(f"✓ Added course: {course_data['name']}")
    
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
    
    print(f"\n✓ Data saved to {filename}")
    return filename

def load_data_from_json(filename="data/schedule_data.json"):
    """Load data from JSON file"""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Data file {filename} not found")
    
    with open(filename, "r") as f:
        data = json.load(f)
    
    return data

def interactive_data_collection():
    """Main interactive data collection flow"""
    print("\n" + "=" * 70)
    print("UNIVERSITY COURSE SCHEDULING - DATA COLLECTION")
    print("=" * 70)
    print("\nThis wizard will help you input all the required data.")
    print("You can also load data from an existing JSON file.\n")
    
    choice = input("Do you want to (1) Enter new data or (2) Load from file? [1/2]: ").strip()
    
    if choice == "2":
        filename = input("Enter JSON file path (default: data/schedule_data.json): ").strip()
        if not filename:
            filename = "data/schedule_data.json"
        
        try:
            data = load_data_from_json(filename)
            print(f"\n✓ Loaded data from {filename}")
            print(f"  Professors: {len(data['professors'])}")
            print(f"  Rooms: {len(data['rooms'])}")
            print(f"  Courses: {len(data['courses'])}")
            return data
        except FileNotFoundError:
            print(f"\n✗ File not found: {filename}")
            print("Switching to data entry mode...\n")
            choice = "1"
    
    if choice == "1":
        # Collect data
        professors = collect_professors()
        rooms = collect_rooms()
        courses = collect_courses()
        
        # Save to JSON
        print("\n" + "=" * 70)
        print("SAVING DATA")
        print("=" * 70)
        
        save_choice = input("\nDo you want to save this data? [y/n]: ").strip().lower()
        if save_choice == 'y':
            filename = input("Enter filename (default: data/schedule_data.json): ").strip()
            if not filename:
                filename = "data/schedule_data.json"
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
