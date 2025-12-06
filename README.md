# University Course Scheduling System - User Guide

## Overview
This system helps you create optimal course schedules using various AI algorithms. All data is now collected interactively or loaded from JSON files - **no hardcoded data**!

## Quick Start

### Option 1: Use Sample Data
```bash
python main.py
```
When prompted, choose option `2` to load from file, then enter:
```
data/sample_data.json
```

### Option 2: Enter Your Own Data
```bash
python main.py
```
When prompted, choose option `1` and follow the interactive wizard to enter:
- Professor information
- Room information  
- Course information

The system will save your data to a JSON file for future use.

## Data Format

### JSON File Structure
```json
{
  "professors": [...],
  "rooms": [...],
  "courses": [...]
}
```

See `data/sample_data.json` for a complete example.

### Professor Fields
- `professor_id`: Unique identifier (e.g., "prof001")
- `name`: Full name
- `department`: Department name
- `courses`: List of course IDs they can teach
- `max_hours`: Maximum teaching hours per week (default: 12)
- `preferences`:
  - `preferred_days`: List of preferred days (e.g., ["monday", "wednesday"])
  - `preferred_times`: List of preferred times (e.g., ["morning", "afternoon"])

### Room Fields
- `room_id`: Unique identifier (e.g., "room101")
- `name`: Room name
- `capacity`: Maximum number of students
- `room_type`: Type of room (e.g., "lecture_hall", "lab")
- `features`: List of features (e.g., ["projector", "whiteboard"])
- `building`: Building name
- `cost_per_hour`: Cost per hour (default: 10.0)

### Course Fields
- `course_id`: Unique identifier (e.g., "cs101")
- `name`: Course name
- `department`: Department name
- `credits`: Number of credits (default: 3)
- `students`: Number of enrolled students
- `course_type`: Type of course (e.g., "lecture", "lab")
- `professors`: List of professor IDs who can teach this course
- `prerequisites`: List of prerequisite course IDs (optional)
- `preferred_times`: List of preferred times (e.g., ["morning"])
- `required_rooms`: List of required room features (e.g., ["projector"])

## Algorithms Available

1. **CSP (Constraint Satisfaction Problem)**: Fast, finds any valid solution
2. **Genetic Algorithm**: Evolutionary approach, finds high-quality solutions
3. **A* Search**: Optimal search with heuristics
4. **Hill Climbing**: Local optimization
5. **BFS (Breadth-First Search)**: Minimal-depth solution
6. **Iterative Deepening**: Memory-efficient complete search
7. **UCS (Uniform Cost Search)**: Minimizes scheduling costs

## Output

The best schedule will be:
1. Displayed on screen
2. Saved to `output/schedule.txt`

## Tips

- Start with the sample data to understand the format
- Save your custom data to JSON files for reuse
- Use descriptive IDs for easy reference
- Ensure professor course lists match actual course IDs
- Make sure room capacities exceed course enrollment

## Troubleshooting

**Q: No valid schedule found?**
- Check that professors can teach the courses assigned to them
- Ensure room capacities are sufficient
- Verify there are enough time slots for all courses

**Q: Empty schedule with positive fitness?**
- This bug has been fixed! Empty schedules now get -10,000 fitness score

**Q: Schedule shows "No classes scheduled" but says courses are assigned?**
- This display bug has been fixed! Courses now show correctly on their assigned days
