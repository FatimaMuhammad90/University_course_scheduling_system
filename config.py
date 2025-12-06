"""
Configuration file for University Scheduling System
All tunable parameters go here
"""

# ============================================
# ALGORITHM PARAMETERS
# ============================================
ALGORITHM_CONFIG = {
    'csp': {
        'max_backtracks': 1000,
        'use_mrv': True,           # Minimum Remaining Values heuristic
        'use_degree': True,        # Degree heuristic
        'use_lcv': True,           # Least Constraining Value
        'timeout': 30,             # seconds
    },
    
    'genetic': {
        'population_size': 100,
        'generations': 1000,
        'mutation_rate': 0.15,
        'crossover_rate': 0.85,
        'elitism_count': 5,        # Keep top 5 each generation
        'tournament_size': 3,
    },
    
    'a_star': {
        'heuristic_weight': 1.0,
        'walking_weight': 0.7,     # Weight for student walking distance
        'preference_weight': 0.3,  # Weight for professor preferences
    },
    
    'hill_climbing': {
        'max_iterations': 500,
        'restarts': 10,            # Random restarts to avoid local maxima
        'neighbor_size': 20,       # Number of neighbors to generate
    },
    
    'bfs': {
        'max_depth': 10,
        'max_nodes': 10000,
    },
    
    'ucs': {
        'room_cost_weight': 1.0,
        'time_pref_weight': 0.5,
    }
}

# ============================================
# SCHEDULING PARAMETERS
# ============================================
TIME_SLOTS = [
    "8:00-9:30",   # Slot 0
    "9:30-11:00",  # Slot 1
    "11:00-12:30", # Slot 2
    "13:00-14:30", # Slot 3
    "14:30-16:00", # Slot 4
    "16:00-17:30", # Slot 5
]

DAYS = [
    "monday",
    "tuesday", 
    "wednesday",
    "thursday",
    "friday"
]

# ============================================
# CONSTRAINTS & PENALTIES
# ============================================
CONSTRAINTS = {
    'hard': {
        'room_capacity': True,
        'no_double_booking': True,
        'professor_availability': True,
        'time_conflict': True,
    },
    
    'soft': {
        'room_preference_penalty': 10,      # Points deducted
        'time_preference_penalty': 5,
        'consecutive_classes_bonus': 15,    # Points added
        'department_cluster_bonus': 20,
    }
}

# ============================================
# FIXED SETTINGS
# ============================================
SLOT_DURATION = 1.5  # hours
MAX_PROFESSOR_HOURS = 12  # per week
MIN_STUDENTS_PER_COURSE = 10
MAX_STUDENTS_PER_ROOM = 300