import copy
class Schedule:
    def __init__(self, courses=None, rooms=None, professors=None):
        self.courses = courses or []
        self.rooms = rooms or []
        self.professors = professors or []
        
        # Assignment tracking
        self.assignments = []  # List of assignment dicts
        self.fitness = 0
        self.constraints_violated = 0
        
    def add_assignment(self, course, room, professor, day, time_slot):
        assignment = {
            'course': course,
            'room': room,
            'professor': professor,
            'day': day,
            'time_slot': time_slot,
            'course_id': course.course_id,
            'room_id': room.room_id,
            'professor_id': professor.professor_id
        }
        
        # Update objects
        course.assigned_time = time_slot
        course.assigned_day = day
        course.assigned_room = room
        course.assigned_professor = professor
        
        room.book(day, time_slot, course.course_id)
        professor.assign_course(day, time_slot, course.course_id, room.room_id)
        
        self.assignments.append(assignment)
    
    def remove_assignment(self, assignment):
        # Remove from course
        assignment['course'].assigned_time = None
        assignment['course'].assigned_day = None
        assignment['course'].assigned_room = None
        assignment['course'].assigned_professor = None
        
        # Remove from room schedule
        day = assignment['day']
        time_slot = assignment['time_slot']
        if day in assignment['room'].schedule:
            if time_slot in assignment['room'].schedule[day]:
                del assignment['room'].schedule[day][time_slot]
        
        # Remove from professor schedule
        prof_schedule = assignment['professor'].schedule.get(day, [])
        assignment['professor'].schedule[day] = [
            slot for slot in prof_schedule 
            if not (slot[0] == time_slot and slot[1] == assignment['course_id'])
        ]
        assignment['professor'].total_hours -= 1.5
        
        # Remove from assignments list
        self.assignments.remove(assignment)
    
    def is_valid(self):
        violations = 0
        
        # Check each assignment
        for i, assign1 in enumerate(self.assignments):
            for j, assign2 in enumerate(self.assignments):
                if i >= j:
                    continue
                
                # Same time and day check
                if (assign1['day'] == assign2['day'] and 
                    assign1['time_slot'] == assign2['time_slot']):
                    
                    # Room conflict
                    if assign1['room'] == assign2['room']:
                        violations += 1
                    
                    # Professor conflict
                    if assign1['professor'] == assign2['professor']:
                        violations += 1
        
        # Check room capacities
        for assignment in self.assignments:
            if assignment['course'].students > assignment['room'].capacity:
                violations += 1
        
        # Check professor availability
        for professor in self.professors:
            if professor.is_overloaded():
                violations += 1
        
        self.constraints_violated = violations
        return violations == 0
    
    def calculate_fitness(self):

        if not self.is_valid():
            self.fitness = -1000  # Invalid schedule penalty
            return self.fitness
        
        score = 1000  # Base score for valid schedule
        
        # 1. Room utilization bonus
        for room in self.rooms:
            score += room.get_utilization(30) * 0.5  # 30 total slots
        
        # 2. Professor preference bonus
        for assignment in self.assignments:
            pref_score = assignment['professor'].get_preference_score(
                assignment['day'], assignment['time_slot']
            )
            score += pref_score * 10
        
        # 3. Student walking distance penalty (simplified)
        # Group courses by department and time proximity
        dept_courses = {}
        for assignment in self.assignments:
            dept = assignment['course'].department
            if dept not in dept_courses:
                dept_courses[dept] = []
            dept_courses[dept].append(assignment)
        
        # Penalize if same department courses are far apart
        for dept, assignments in dept_courses.items():
            if len(assignments) > 1:
                buildings = set(a['room'].building for a in assignments)
                if len(buildings) > 1:
                    score -= 20 * (len(buildings) - 1)
        
        # 4. Time preference bonus
        for assignment in self.assignments:
            course = assignment['course']
            if course.preferred_times:
                time_of_day = "morning" if assignment['time_slot'] <= 2 else "afternoon"
                if time_of_day in course.preferred_times:
                    score += 15
        
        self.fitness = score
        return score
    
    def __str__(self):
        output = "=" * 60 + "\n"
        output += "COURSE SCHEDULE\n"
        output += "=" * 60 + "\n"
        
        # Group by day
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = ["8:00-9:30", "9:30-11:00", "11:00-12:30", 
                     "13:00-14:30", "14:30-16:00", "16:00-17:30"]
        
        for day in days:
            output += f"\n{day}:\n"
            output += "-" * 40 + "\n"
            
            day_assignments = [a for a in self.assignments if a['day'] == day]
            if not day_assignments:
                output += "  No classes scheduled\n"
                continue
            
            for time_idx in range(len(time_slots)):
                time_assignments = [a for a in day_assignments if a['time_slot'] == time_idx]
                if time_assignments:
                    for assign in time_assignments:
                        output += f"  {time_slots[time_idx]}: "
                        output += f"{assign['course'].course_id} - {assign['course'].name}\n"
                        output += f"      Room: {assign['room'].room_id}, "
                        output += f"Prof: {assign['professor'].name}\n"
        
        output += f"\nFitness Score: {self.fitness:.2f}\n"
        output += f"Constraints Violated: {self.constraints_violated}\n"
        output += "=" * 60
        
        return output
    
    def copy(self):
   
        new_schedule = Schedule(
            courses=copy.deepcopy(self.courses),
            rooms=copy.deepcopy(self.rooms),
            professors=copy.deepcopy(self.professors)
        )
        
        # Recreate assignments
        for assignment in self.assignments:
            # Find corresponding objects in copied lists
            course = next(c for c in new_schedule.courses if c.course_id == assignment['course_id'])
            room = next(r for r in new_schedule.rooms if r.room_id == assignment['room_id'])
            professor = next(p for p in new_schedule.professors if p.professor_id == assignment['professor_id'])
            
            new_schedule.add_assignment(
                course, room, professor,
                assignment['day'], assignment['time_slot']
            )
        
        new_schedule.fitness = self.fitness
        new_schedule.constraints_violated = self.constraints_violated
        
        return new_schedule