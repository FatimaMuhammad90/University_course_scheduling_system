import random
import config
from models import schedule

class genetic:
    def __init__(self, schedule_obj):
        self.schedule = schedule_obj
        self.population = []
        self.best_fitness = 0
        self.best_schedule = None
    
    def create_population(self):
        """Create initial population of schedules"""
        print(f"Creating population of {config.ALGORITHM_CONFIG['genetic']['population_size']}...")
        self.population = []
        
        for _ in range(config.ALGORITHM_CONFIG['genetic']['population_size']):
            individual = self.create_random_schedule()
            if individual.is_valid():
                individual.calculate_fitness()
                self.population.append(individual)
        
        # Sort by fitness
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.best_schedule = self.population[0]
        self.best_fitness = self.best_schedule.fitness
    
    def create_random_schedule(self):
        """Create a random valid schedule"""
        new_schedule = self.schedule.copy()
        
        for course in new_schedule.courses:
            if course.assigned_time is not None:
                continue
            
            # Find available rooms
            available_rooms = [r for r in new_schedule.rooms if r.can_accommodate(course)]
            if not available_rooms:
                continue
            
            # Find available professors
            available_profs = [p for p in new_schedule.professors 
                              if p.can_teach(course.course_id)]
            if not available_profs:
                continue
            
            # Try to find a valid time slot
            max_attempts = 100
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
    
    def evolve(self, generations=None):
        """Run genetic algorithm evolution"""
        if generations is None:
            generations = config.ALGORITHM_CONFIG['genetic']['generations']
        
        self.create_population()
        
        print(f"Starting evolution for {generations} generations...")
        for gen in range(generations):
            # Selection
            parents = self.selection()
            
            # Create new generation
            new_population = []
            
            # Elitism: keep best individuals
            elitism_count = config.ALGORITHM_CONFIG['genetic']['elitism_count']
            new_population.extend(self.population[:elitism_count])
            
            # Create offspring
            while len(new_population) < len(self.population):
                parent1, parent2 = random.sample(parents, 2)
                
                # Crossover
                child = self.crossover(parent1, parent2)
                
                # Mutation
                if random.random() < config.ALGORITHM_CONFIG['genetic']['mutation_rate']:
                    child = self.mutate(child)
                
                child.calculate_fitness()
                new_population.append(child)
            
            # Replace population
            self.population = new_population
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            
            # Update best
            if self.population[0].fitness > self.best_fitness:
                self.best_schedule = self.population[0]
                self.best_fitness = self.best_schedule.fitness
            
            # Print progress
            if gen % 100 == 0:
                avg_fitness = sum(s.fitness for s in self.population) / len(self.population)
                print(f"Gen {gen}: Best={self.best_fitness:.1f}, Avg={avg_fitness:.1f}")
        
        print(f"Evolution complete. Best fitness: {self.best_fitness:.2f}")
        return self.best_schedule
    
    def selection(self):
        """Tournament selection"""
        tournament_size = config.ALGORITHM_CONFIG['genetic']['tournament_size']
        selected = []
        
        while len(selected) < len(self.population):
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1, parent2):
        """Uniform crossover between two schedules"""
        child = parent1.copy()
        
        # For each course, randomly choose assignment from either parent
        for course in child.courses:
            if random.random() < 0.5:
                # Get assignment from parent2
                assignment2 = next((a for a in parent2.assignments 
                                  if a['course_id'] == course.course_id), None)
                if assignment2:
                    # Remove current assignment if exists
                    current_assignment = next((a for a in child.assignments 
                                             if a['course_id'] == course.course_id), None)
                    if current_assignment:
                        child.remove_assignment(current_assignment)
                    
                    # Add assignment from parent2
                    room = next(r for r in child.rooms if r.room_id == assignment2['room_id'])
                    prof = next(p for p in child.professors if p.professor_id == assignment2['professor_id'])
                    
                    if (room.is_available(assignment2['day'], assignment2['time_slot']) and
                        prof.is_available(assignment2['day'], assignment2['time_slot'])):
                        child.add_assignment(course, room, prof, 
                                           assignment2['day'], assignment2['time_slot'])
        
        return child
    
    def mutate(self, schedule_obj):
        """Mutation: randomly change some assignments"""
        mutated = schedule_obj.copy()
        
        # Randomly select some courses to mutate
        mutation_rate = 0.1  # 10% of courses
        courses_to_mutate = [c for c in mutated.courses 
                           if random.random() < mutation_rate]
        
        for course in courses_to_mutate:
            # Remove current assignment if exists
            current_assignment = next((a for a in mutated.assignments 
                                     if a['course_id'] == course.course_id), None)
            if current_assignment:
                mutated.remove_assignment(current_assignment)
            
            # Try to find new assignment
            available_rooms = [r for r in mutated.rooms if r.can_accommodate(course)]
            available_profs = [p for p in mutated.professors 
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
                        mutated.add_assignment(course, room, prof, day, time_slot)
                        break
        
        return mutated