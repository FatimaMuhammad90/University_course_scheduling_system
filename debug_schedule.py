"""
Debug why 4/4 schedule is invalid
"""
import sys
sys.path.insert(0, '.')

from models import course, room, professor, schedule

# Create sample data
prof1 = professor(
    professor_id="prof001",
    name="Dr. Test",
    department="CS",
    courses=["cs101", "cs102", "cs103", "cs104"],
    max_hours=12,
    preferences={"preferred_days": ["monday"], "preferred_times": ["morning"]}
)

room1 = room(
    room_id="room101",
    name="Room 101",
    capacity=50,
    room_type="lecture_hall",
    features=["projector"],
    building="Main",
    cost_per_hour=10.0
)

courses = [
    course(
        course_id=f"cs10{i}",
        name=f"Course {i}",
        department="CS",
        credits=3,
        students=30,
        course_type="lecture",
        professors=["prof001"],
        preferred_times=["morning"],
        required_rooms=["projector"]
    ) for i in range(1, 5)
]

test_schedule = schedule(
    courses=courses,
    rooms=[room1],
    professors=[prof1]
)

# Add all 4 assignments across different days
days = ["monday", "tuesday", "wednesday", "thursday"]
for i in range(4):
    test_schedule.add_assignment(
        courses[i], room1, prof1, 
        days[i], 0
    )

print("Schedule with 4/4 courses:")
print(f"  Assignments: {len(test_schedule.assignments)}")
print(f"  Is Valid: {test_schedule.is_valid()}")
print(f"  Constraints Violated: {test_schedule.constraints_violated}")
print(f"  Professor hours: {prof1.total_hours}/{prof1.max_hours}")
print(f"  Professor overloaded: {prof1.is_overloaded()}")

# Check each assignment
print("\nAssignments:")
for i, assign in enumerate(test_schedule.assignments):
    print(f"  {i+1}. {assign['course_id']} - {assign['day']} slot {assign['time_slot']}")
    print(f"     Room: {assign['room_id']}, Prof: {assign['professor_id']}")
    print(f"     Students: {assign['course'].students}, Room capacity: {assign['room'].capacity}")
