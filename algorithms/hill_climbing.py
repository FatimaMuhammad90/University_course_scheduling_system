import random
import config
from models import schedule

class hill_climbing:
    def __init__(self, schedule_obj):
        self.schedule = schedule_obj
        self.best_schedule = schedule_obj
        self.best_fitness = schedule_obj.calculate_fitness()
    
    def optimize(self):
        print("Starting Hill Climbing optimization...")
        
        current = self.schedule.copy()
        current_fitness = current.calculate_fitness()
        
        restarts = config.ALGORITHM_CONFIG['hill_climbing']['restarts']
        
        for restart in range(restarts):
            print(f"\nRestart {restart + 1}/{restarts}")
            
            # Random initialization for this restart
            if restart > 0:
                current = self.create_random_schedule()
                current_fitness = current.calculate_fitness()
            
            iteration = 0
            stuck_count = 0
            
            while iteration < config.ALGORITHM_CONFIG['hill_climbing']['max_iterations']:
                iteration += 1
                
                # Generate neighbors
                neighbors = self.generate_neighbors(current)
                
                # Find best neighbor
                best_neighbor = None
                best_neighbor_fitness = -float('inf')
                
                for neighbor in neighbors:
                    fitness = neighbor.calculate_fitness()
                    if fitness > best_neighbor_fitness:
                        best_neighbor = neighbor
                        best_neighbor_fitness = fitness
                
                # Check if we should move
                if best_neighbor_fitness > current_fitness:
                    current = best_neighbor
                    current_fitness = best_neighbor_fitness
                    stuck_count = 0
                    
                    # Update global best
                    if current_fitness > self.best_fitness:
                        self.best_schedule = current.copy()
                        self.best_fitness = current_fitness
                        print(f"  ↗ New best: {self.best_fitness:.2f}")
                else:
                    stuck_count += 1
                
                # If stuck for too long, break
                if stuck_count > 50:
                    break
            
            print(f"  Restart best: {current_fitness:.2f}")
        
        print(f"\n Hill Climbing complete. Best fitness: {self.best_fitness:.2f}")
        return self.best_schedule
    
    def generate_neighbors(self, schedule_obj):
        """Generate neighboring schedules"""
        neighbors = []
        neighbor_size = config.ALGORITHM_CONFIG['hill_climbing']['neighbor_size']
        
        for _ in range(neighbor_size):
            neighbor = schedule_obj.copy()
            
            # Choose random operation
            operation = random.choice(['swap', 'move', 'reschedule'])
            
            if operation == 'swap' and len(neighbor.assignments) >= 2:
                # Swap two assignments
                idx1, idx2 = random.sample(range(len(neighbor.assignments)), 2)
                assign1 = neighbor.assignments[idx1]
                assign2 = neighbor.assignments[idx2]
                
                # Check if swap is valid
                if (assign1['room'].can_accommodate(assign2['course']) and
                    assign2['room'].can_accommodate(assign1['course']) and
                    assign1['professor'].can_teach(assign2['course'].course_id) and
                    assign2['professor'].can_teach(assign1['course'].course_id) and
                    assign1['room'].is_available(assign1['day'], assign1['time_slot']) and
                    assign2['room'].is_available(assign2['day'], assign2['time_slot'])):
                    
                    # Remove assignments
                    neighbor.remove_assignment(assign1)
                    neighbor.remove_assignment(assign2)
                    
                    # Add swapped assignments
                    neighbor.add_assignment(assign2['course'], assign1['room'], 
                                          assign1['professor'], assign1['day'], 
                                          assign1['time_slot'])
                    neighbor.add_assignment(assign1['course'], assign2['room'], 
                                          assign2['professor'], assign2['day'], 
                                          assign2['time_slot'])
            
            elif operation == 'move':
                # Move an assignment to different time
                if neighbor.assignments:
                    assign = random.choice(neighbor.assignments)
                    neighbor.remove_assignment(assign)
                    
                    # Try to find new time
                    max_attempts = 20
                    for _ in range(max_attempts):
                        new_day = random.choice(config.DAYS)
                        new_time = random.randint(0, len(config.TIME_SLOTS) - 1)
                        
                        if (assign['room'].is_available(new_day, new_time) and
                            assign['professor'].is_available(new_day, new_time)):
                            neighbor.add_assignment(assign['course'], assign['room'],
                                                  assign['professor'], new_day, new_time)
                            break
            
            elif operation == 'reschedule':
                # Completely reschedule a random course
                if neighbor.assignments:
                    assign = random.choice(neighbor.assignments)
                    neighbor.remove_assignment(assign)
                    
                    # Find new assignment
                    course = assign['course']
                    available_rooms = [r for r in neighbor.rooms 
                                     if r.can_accommodate(course)]
                    available_profs = [p for p in neighbor.professors 
                                     if p.can_teach(course.course_id)]
                    
                    if available_rooms and available_profs:
                        max_attempts = 30
                        for _ in range(max_attempts):
                            room = random.choice(available_rooms)
                            prof = random.choice(available_profs)
                            day = random.choice(config.DAYS)
                            time_slot = random.randint(0, len(config.TIME_SLOTS) - 1)
                            
                            if (room.is_available(day, time_slot) and 
                                prof.is_available(day, time_slot)):
                                neighbor.add_assignment(course, room, prof, day, time_slot)
                                break
            
            neighbors.append(neighbor)
        
        return neighbors
    
    def create_random_schedule(self):
        """Create random valid schedule"""
        new_schedule = self.schedule.copy()
        
        # Clear all assignments
        for assignment in new_schedule.assignments[:]:
            new_schedule.remove_assignment(assignment)
        
        # Randomly assign courses
        for course in new_schedule.courses:
            available_rooms = [r for r in new_schedule.rooms 
                             if r.can_accommodate(course)]
            available_profs = [p for p in new_schedule.professors 
                             if p.can_teach(course.course_id)]
            
            if available_rooms and available_profs:
                max_attempts = 50
                for _ in range(max_attempts):
                    room = random.choice(available_rooms)
                    prof = random.choice(available_profs)
                    day = random.choice(config.DAYS)
                    time_slot = random.randint(0, len(config.TIME_SLOTS) - 1)
                    
                    if (room.is_available(day, time_slot) and 
                        prof.is_available(day, time_slot)):
                        new_schedule.add_assignment(course, room, prof, day, time_slot)
                        break
        
        return new_schedule