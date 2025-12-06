# Create sample data
from models import Course, Room, Professor, Schedule

# Create courses
cs101 = Course(
    course_id="CS101",
    name="Introduction to Programming",
    department="Computer Science",
    credits=3,
    students=60,
    course_type="lecture",
    professors=["PROF001", "PROF002"],
    preferred_times=["morning"]
)

# Create room
room101 = Room(
    room_id="SCI-101",
    name="Science Building 101",
    capacity=80,
    room_type="lecture_hall",
    features=["projector", "whiteboard", "microphone"],
    building="Science Building",
    floor=1,
    cost_per_hour=10.0
)

# Create professor
prof_smith = Professor(
    professor_id="PROF001",
    name="Dr. Smith",
    department="Computer Science",
    courses=["CS101", "CS201"],
    max_hours=12,
    office_location="SCI-305"
)

# Create schedule
schedule = Schedule(courses=[cs101], rooms=[room101], professors=[prof_smith])

# Make an assignment
schedule.add_assignment(cs101, room101, prof_smith, "Monday", 0)  # 8:00-9:30 Monday

# Check validity
print(f"Schedule valid: {schedule.is_valid()}")
print(f"Fitness: {schedule.calculate_fitness()}")

# Print schedule
print(schedule)