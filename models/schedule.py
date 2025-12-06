import copy
import config

class schedule:
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
        """
        Calculate fitness score for the schedule.
        CRITICAL: Empty schedules get very negative scores to prevent algorithms
        from finding "solutions" with zero assignments.
        """
        # Invalid schedules get the worst score
        if not self.is_valid():
            self.fitness = config.FITNESS_WEIGHTS['hard_constraint_violation']
            return self.fitness
        
        # START WITH NEGATIVE BASE SCORE
        # This ensures that only schedules with actual assignments get positive scores
        score = -1000
        
        # HEAVY PENALTY FOR INCOMPLETE SCHEDULE
        scheduled_courses = len(self.assignments)
        total_courses = len(self.courses)
        
        if scheduled_courses == 0:
            # EMPTY SCHEDULE GETS VERY LOW SCORE
            self.fitness = config.FITNESS_WEIGHTS['empty_schedule_penalty']
            return self.fitness
        
        # BONUS FOR COMPLETENESS
        # This is the main way to get a positive score - by actually scheduling courses
        completion_ratio = scheduled_courses / total_courses
        score += completion_ratio * 2000  # Big bonus for complete schedules
        
        # Additional bonuses for quality assignments
        for assignment in self.assignments:
            course = assignment['course']
            room = assignment['room']
            prof = assignment['professor']
            day = assignment['day']
            time_slot = assignment['time_slot']
            
            # Room capacity fitness
            utilization = course.students / room.capacity
            if utilization > 0.8:
                score += 20
            elif utilization > 0.5:
                score += 10
            elif utilization < 0.3:
                score -= 10  # Penalize underutilization
            
            # Professor preferences
            pref_score = prof.get_preference_score(day, time_slot)
            score += pref_score * 10
            
            # Course time preferences
            time_of_day = "morning" if time_slot <= 2 else "afternoon"
            if time_of_day in course.preferred_times:
                score += config.FITNESS_WEIGHTS['time_preference_bonus']
        
        # Department clustering bonus
        dept_assignments = {}
        for assignment in self.assignments:
            dept = assignment['course'].department
            building = assignment['room'].building
            if dept not in dept_assignments:
                dept_assignments[dept] = set()
            dept_assignments[dept].add(building)
        
        for dept, buildings in dept_assignments.items():
            if len(buildings) == 1:
                score += config.FITNESS_WEIGHTS['department_clustering_bonus']
        
        self.fitness = score
        return score
    
    def calculate_total_cost(self):
        """Calculate total room rental cost per week"""
        total = 0
        for assignment in self.assignments:
            # Each class is 1.5 hours
            total += assignment['room'].cost_per_hour * 1.5
        return total
    
    def get_cost_breakdown(self):
        """Get cost breakdown by room"""
        breakdown = {}
        for assignment in self.assignments:
            room_id = assignment['room'].room_id
            cost = assignment['room'].cost_per_hour * 1.5
            if room_id not in breakdown:
                breakdown[room_id] = {
                    'room_name': assignment['room'].name,
                    'count': 0,
                    'total_cost': 0
                }
            breakdown[room_id]['count'] += 1
            breakdown[room_id]['total_cost'] += cost
        return breakdown
    
    def calculate_walking_distance(self):
        """Calculate walking distance score based on building transitions"""
        # Building distance map (in meters)
        building_distances = {
            ('Science Building', 'Engineering Building'): 200,
            ('Engineering Building', 'Science Building'): 200,
            ('Science Building', 'Arts Building'): 150,
            ('Arts Building', 'Science Building'): 150,
            ('Engineering Building', 'Arts Building'): 250,
            ('Arts Building', 'Engineering Building'): 250,
        }
        
        total_distance = 0
        transitions = self.get_building_transitions()
        
        for day, day_transitions in transitions.items():
            for trans in day_transitions:
                distance = building_distances.get((trans['from'], trans['to']), 100)
                total_distance += distance
        
        return total_distance
    
    def get_building_transitions(self):
        """Get building transitions students must make each day"""
        transitions = {}
        
        # Group assignments by day
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
            day_assignments = sorted(
                [a for a in self.assignments if a['day'] == day],
                key=lambda x: x['time_slot']
            )
            
            day_transitions = []
            for i in range(len(day_assignments) - 1):
                curr_building = day_assignments[i]['room'].building
                next_building = day_assignments[i+1]['room'].building
                
                if curr_building != next_building:
                    day_transitions.append({
                        'from': curr_building,
                        'to': next_building,
                        'time': day_assignments[i]['time_slot']
                    })
            
            if day_transitions:
                transitions[day] = day_transitions
        
        return transitions
    
    def get_preference_satisfaction(self):
        """Calculate percentage of preferences satisfied"""
        if not self.assignments:
            return 0.0
        
        satisfied = 0
        total = 0
        
        for assignment in self.assignments:
            prof = assignment['professor']
            day = assignment['day']
            time_slot = assignment['time_slot']
            
            # Check day preference
            if 'preferred_days' in prof.preferences:
                total += 1
                if day in prof.preferences['preferred_days']:
                    satisfied += 1
            
            # Check time preference
            if 'preferred_times' in prof.preferences:
                total += 1
                time_of_day = "morning" if time_slot <= 2 else "afternoon"
                if time_of_day in prof.preferences['preferred_times']:
                    satisfied += 1
        
        return (satisfied / total * 100) if total > 0 else 0.0
    
    def compare_to(self, other_schedule):
        """Compare this schedule to another (for Hill Climbing)"""
        improvements = {
            'fitness_change': self.fitness - other_schedule.fitness,
            'assignments_changed': 0,
            'improvements': []
        }
        
        # Count changed assignments
        for assignment in self.assignments:
            course_id = assignment['course_id']
            # Find same course in other schedule
            other_assign = next(
                (a for a in other_schedule.assignments if a['course_id'] == course_id),
                None
            )
            if other_assign:
                if (assignment['room_id'] != other_assign['room_id'] or
                    assignment['day'] != other_assign['day'] or
                    assignment['time_slot'] != other_assign['time_slot']):
                    improvements['assignments_changed'] += 1
        
        # Identify improvements
        if improvements['fitness_change'] > 0:
            improvements['improvements'].append(f"Fitness improved by {improvements['fitness_change']:.2f}")
        
        pref_change = self.get_preference_satisfaction() - other_schedule.get_preference_satisfaction()
        if pref_change > 0:
            improvements['improvements'].append(f"Preference satisfaction improved by {pref_change:.1f}%")
        
        return improvements
    
    def __str__(self):
        output = "=" * 60 + "\n"
        output += "COURSE SCHEDULE\n"
        output += "=" * 60 + "\n"
        
        # Group by day - FIX: use lowercase for comparison since assignments store lowercase days
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        days_display = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        time_slots = ["8:00-9:30", "9:30-11:00", "11:00-12:30", 
                     "13:00-14:30", "14:30-16:00", "16:00-17:30"]
        
        for i, day in enumerate(days):
            output += f"\n{days_display[i]}:\n"
            output += "-" * 40 + "\n"
            
            # Now this comparison will work correctly
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
        output += f"Courses Scheduled: {len(self.assignments)}/{len(self.courses)}\n"
        output += "=" * 60
        
        return output
    
    def copy(self):
        """Create a deep copy of the schedule"""
        new_schedule = schedule(
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