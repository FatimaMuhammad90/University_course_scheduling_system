from models import schedule
import config
import time

class csp:
    def __init__(self, schedule_obj):
        self.schedule = schedule_obj
        self.variables = []  # Courses to schedule
        self.domains = {}    # Possible values for each course
        self.constraints = []
        self.solution = None

    def is_goal(self, schedule_obj):
        """Check if ALL courses are scheduled"""
        return all(c.assigned_time is not None for c in schedule_obj.courses)

    # starter
    def solve(self):
        print("Starting CSP solver...")
        start_time = time.time()
        

        self.variables = [c for c in self.schedule.courses if c.assigned_time is None]
        
        for course in self.variables:
            self.domains[course.course_id] = self.get_domain_values(course)
        
        self.ac3()
        
        # Start backtracking search
        assignments = {}
        self.solution = self.backtrack(assignments, start_time)
        
        if self.solution:
            elapsed = time.time() - start_time
            print(f"CSP solved in {elapsed:.2f} seconds")
            print(f"   Assignments made: {len(self.solution.assignments)}")
            print(f"   Fitness: {self.solution.calculate_fitness():.2f}")
        else:
            print(" CSP could not find solution")
        
        return self.solution
    
    def get_domain_values(self, course):
        """Get all possible assignments for a course"""
        domain = []
        
        for room in self.schedule.rooms:
            if not room.can_accommodate(course):
                continue
            
            for prof in self.schedule.professors:
                if not prof.can_teach(course.course_id):
                    continue
                
                for day in config.DAYS:
                    for time_slot in range(len(config.TIME_SLOTS)):
                        if (room.is_available(day, time_slot) and 
                            prof.is_available(day, time_slot)):
                            domain.append((room, prof, day, time_slot))
        
        return domain
    
    def ac3(self):
        queue = []
        
        for xi in self.variables:
            for xj in self.variables:
                if xi != xj:
                    queue.append((xi.course_id, xj.course_id))
        
        while queue:
            xi_id, xj_id = queue.pop(0)
            if self.revise(xi_id, xj_id):
                if not self.domains[xi_id]:
                    return False
                for xk in self.variables:
                    if xk.course_id != xi_id and xk.course_id != xj_id:
                        queue.append((xk.course_id, xi_id))
        
        return True
    
    def revise(self, xi_id, xj_id):
        revised = False
        
        for val_i in self.domains[xi_id][:]:
            if not self.has_support(xi_id, val_i, xj_id):
                self.domains[xi_id].remove(val_i)
                revised = True
        
        return revised
    
    def has_support(self, xi_id, val_i, xj_id):
        room_i, prof_i, day_i, time_i = val_i
        
        for val_j in self.domains[xj_id]:
            room_j, prof_j, day_j, time_j = val_j
            #constriants checker
            if day_i == day_j and time_i == time_j:
                if room_i.room_id == room_j.room_id:
                    continue  # Room conflict
                if prof_i.professor_id == prof_j.professor_id:
                    continue  # Professor conflict
            
            return True
        
        return False
    
    def backtrack(self, assignments, start_time):
        if time.time() - start_time > config.ALGORITHM_CONFIG['csp']['timeout']:
            return None
        
        if len(assignments) == len(self.variables):
            return self.create_schedule_from_assignments(assignments)
        

        var = self.select_unassigned_variable(assignments)
        
        ordered_values = self.order_domain_values(var, assignments)
        
        for value in ordered_values:
            room, prof, day, time_slot = value
            
            if self.is_consistent(var, value, assignments):
                assignments[var.course_id] = value
                
                inferences = self.forward_check(var, value, assignments)
                if inferences is not None:
                    result = self.backtrack(assignments, start_time)
                    if result is not None:
                        return result
                
                del assignments[var.course_id]
        
        return None
    #MRV
    def select_unassigned_variable(self, assignments):
        unassigned = [v for v in self.variables if v.course_id not in assignments]
        
        if config.ALGORITHM_CONFIG['csp']['use_mrv']:
            unassigned.sort(key=lambda v: len(self.domains[v.course_id]))
        
        return unassigned[0] if unassigned else None
    #LCV
    def order_domain_values(self, var, assignments):
        values = self.domains[var.course_id][:]
        
        if config.ALGORITHM_CONFIG['csp']['use_lcv']:

            values.sort(key=lambda v: self.count_constraints(var, v, assignments))
        
        return values
    
    def count_constraints(self, var, value, assignments):
        count = 0
        room_i, prof_i, day_i, time_i = value
        
        for other_var in self.variables:
            if other_var.course_id == var.course_id or other_var.course_id in assignments:
                continue
            
            for val_j in self.domains[other_var.course_id]:
                room_j, prof_j, day_j, time_j = val_j
                
                if day_i == day_j and time_i == time_j:
                    if room_i.room_id == room_j.room_id:
                        count += 1
                    if prof_i.professor_id == prof_j.professor_id:
                        count += 1
        
        return count
    
    def is_consistent(self, var, value, assignments):
        room_i, prof_i, day_i, time_i = value
        
        for assigned_var_id, assigned_val in assignments.items():
            room_j, prof_j, day_j, time_j = assigned_val
            
            if day_i == day_j and time_i == time_j:
                if room_i.room_id == room_j.room_id:
                    return False
                if prof_i.professor_id == prof_j.professor_id:
                    return False
        
        return True
    #phelaye hi unreaslitic values ko nikal do
    def forward_check(self, var, value, assignments):
        room_i, prof_i, day_i, time_i = value
        pruned = {}
        
        for other_var in self.variables:
            if other_var.course_id == var.course_id or other_var.course_id in assignments:
                continue
            
            to_remove = []
            for val_j in self.domains[other_var.course_id]:
                room_j, prof_j, day_j, time_j = val_j
                
                if day_i == day_j and time_i == time_j:
                    if room_i.room_id == room_j.room_id or prof_i.professor_id == prof_j.professor_id:
                        to_remove.append(val_j)
            
            if to_remove:
                pruned[other_var.course_id] = to_remove
                for val in to_remove:
                    self.domains[other_var.course_id].remove(val)
                
                if not self.domains[other_var.course_id]:
                    for var_id, removed_vals in pruned.items():
                        self.domains[var_id].extend(removed_vals)
                    return None
        
        return pruned
    
    def create_schedule_from_assignments(self, assignments):
        new_schedule = self.schedule.copy()
        
        for course_id, value in assignments.items():
            room, prof, day, time_slot = value
            
            course = next(c for c in new_schedule.courses if c.course_id == course_id)
            room_obj = next(r for r in new_schedule.rooms if r.room_id == room.room_id)
            prof_obj = next(p for p in new_schedule.professors if p.professor_id == prof.professor_id)
            
            new_schedule.add_assignment(course, room_obj, prof_obj, day, time_slot)
        
        return new_schedule