
ALGORITHM_CONFIG = {
    'csp': {
        'max_backtracks': 1000,
        'use_mrv': True,
        'use_degree': True,
        'use_lcv': True,
        'timeout': 30,
    },
    
    'genetic': {
        'population_size': 50,
        'generations': 200,
        'mutation_rate': 0.1,
        'crossover_rate': 0.8,
        'elitism_count': 3,
        'tournament_size': 3,
    },
    
    'a_star': {
        'heuristic_weight': 1.0,
        'walking_weight': 0.7,
        'preference_weight': 0.3,
    },
    
    'hill_climbing': {
        'max_iterations': 500,
        'restarts': 3,
        'neighbor_size': 15,
    },
    
    'bfs': {
        'max_depth': 5,
        'max_nodes': 2000,
    },
    
    'iterative_deepening': {
        'max_depth': 5,
        'depth_increment': 1,
    },
    
    'ucs': {
        'room_cost_weight': 1.0,
        'time_pref_weight': 0.5,
        'walking_cost_weight': 0.3,
    }
}


TIME_SLOTS = [
    "8:00-9:30",  
    "9:30-11:00", 
    "11:00-12:30", 
    "13:00-14:30", 
    "14:30-16:00", 
    "16:00-17:30",
]

DAYS = [
    "monday",
    "tuesday", 
    "wednesday",
    "thursday",
    "friday"
]
SLOT_DURATION = 1.5  
MAX_PROFESSOR_HOURS = 12
WORK_HOURS = {"start": "8:00", "end": "18:00"}

FITNESS_WEIGHTS = {
    'hard_constraint_violation': -10000,
    'empty_schedule_penalty': -10000,
    'incomplete_schedule_penalty': -500,
    'room_capacity_penalty': -50,
    'professor_overload_penalty': -100,
    'time_preference_bonus': 20,
    'room_preference_bonus': 15,
    'consecutive_classes_bonus': 10,
    'department_clustering_bonus': 25,
    'completion_bonus': 1000,
}