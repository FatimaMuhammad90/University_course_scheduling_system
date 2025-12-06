# main.py - Specialized Algorithm Interface
import sys
import os
import time

# Add fallback configuration if config.py doesn't exist
try:
    import config
except ImportError:
    print("Warning: config.py not found, using default configuration")
    
    class SimpleConfig:
        ALGORITHM_CONFIG = {
            'csp': {'max_backtracks': 1000, 'timeout': 30},
            'genetic': {'population_size': 50, 'generations': 200},
            'a_star': {},
            'hill_climbing': {'max_iterations': 500},
            'bfs': {'max_depth': 5, 'max_nodes': 2000},
            'iterative_deepening': {'max_depth': 5},
            'ucs': {}
        }
        TIME_SLOTS = ["8:00-9:30", "9:30-11:00", "11:00-12:30", 
                     "13:00-14:30", "14:30-16:00", "16:00-17:30"]
        DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        FITNESS_WEIGHTS = {
            'hard_constraint_violation': -10000,
            'empty_schedule_penalty': -10000,
            'time_preference_bonus': 20,
            'department_clustering_bonus': 25,
        }
    
    sys.modules['config'] = SimpleConfig()
    import config

from models import schedule
from algorithms import csp, genetic, a_star, hill_climbing, bfs, iterative_deepening, ucs
from data_loader import load_from_json_file
import config

def save_schedule_to_file(schedule_obj, filename="output/schedule.txt"):
    """Save schedule to file"""
    os.makedirs("output", exist_ok=True)
    
    with open(filename, "w") as f:
        f.write(str(schedule_obj))
    
    print(f"\nSchedule saved to {filename}")

# ============================================================================
# MODE 1: QUICK SCHEDULE (BFS)
# ============================================================================
def quick_schedule(data):
    """Get any valid schedule fast using BFS"""
    print("\n" + "=" * 70)
    print("QUICK SCHEDULE")
    print("=" * 70)
    print("Finding a valid schedule quickly...")
    
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    start_time = time.time()
    result = bfs(initial_schedule, max_depth=5)
    elapsed = time.time() - start_time
    
    if result:
        print(f"\n[OK] Schedule generated in {elapsed:.2f} seconds")
        print(f"  Courses Scheduled: {len(result.assignments)}/{len(result.courses)}")
        print(f"  Valid: {result.is_valid()}")
        
        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(result)
        
        save_schedule_to_file(result)
    else:
        print("\n[FAIL] Could not generate schedule")

# ============================================================================
# MODE 2: URGENT SCHEDULING (CSP)
# ============================================================================
def urgent_schedule(data):
    """Emergency scheduling - fastest possible using CSP"""
    print("\n" + "=" * 70)
    print("URGENT SCHEDULING")
    print("=" * 70)
    print("EMERGENCY MODE - Finding fastest solution...")
    
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    csp_solver = csp(initial_schedule)
    start_time = time.time()
    result = csp_solver.solve()
    elapsed = time.time() - start_time
    
    if result:
        print(f"\n[OK] Emergency schedule generated in {elapsed:.2f} seconds")
        print(f"  Courses Scheduled: {len(result.assignments)}/{len(result.courses)}")
        print(f"  Valid: {result.is_valid()}")
        print("\n  Note: This is an emergency schedule.")
        print("     Consider using 'Optimize Preferences' for better quality.")
        
        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(result)
        
        save_schedule_to_file(result)
    else:
        print("\n[FAIL] Could not generate emergency schedule")

# ============================================================================
# MODE 3: OPTIMIZE PREFERENCES (GENETIC ALGORITHM)
# ============================================================================
def optimize_preferences(data):
    """Find best quality schedule considering preferences using Genetic Algorithm"""
    print("\n" + "=" * 70)
    print("OPTIMIZE PREFERENCES")
    print("=" * 70)
    print("Finding high-quality schedule with preference optimization...")
    
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    ga_solver = genetic(initial_schedule)
    start_time = time.time()
    result = ga_solver.evolve(generations=200)
    elapsed = time.time() - start_time
    
    if result:
        pref_satisfaction = result.get_preference_satisfaction()
        
        print(f"\n[OK] Optimized schedule generated in {elapsed:.2f} seconds")
        print(f"\nQuality Metrics:")
        print(f"  Fitness Score: {result.calculate_fitness():.2f}")
        print(f"  Preference Satisfaction: {pref_satisfaction:.1f}%")
        print(f"  Courses Scheduled: {len(result.assignments)}/{len(result.courses)}")
        print(f"  Valid: {result.is_valid()}")
        
        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(result)
        
        save_schedule_to_file(result)
    else:
        print("\n[FAIL] Could not optimize schedule")

# ============================================================================
# MODE 4: MINIMIZE COSTS (UCS)
# ============================================================================
def minimize_costs(data):
    """Budget-conscious scheduling using UCS"""
    print("\n" + "=" * 70)
    print("MINIMIZE COSTS")
    print("=" * 70)
    print("Finding cost-optimized schedule...")
    
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    ucs_solver = ucs(initial_schedule)
    start_time = time.time()
    result = ucs_solver.find_min_cost_schedule()
    elapsed = time.time() - start_time
    
    if result:
        total_cost = result.calculate_total_cost()
        cost_breakdown = result.get_cost_breakdown()
        
        print(f"\n[OK] Cost-optimized schedule generated in {elapsed:.2f} seconds")
        print(f"\nCost Analysis:")
        print(f"  Total Cost per Week: ${total_cost:.2f}")
        print(f"  Annual Cost (30 weeks): ${total_cost * 30:.2f}")
        
        print(f"\n  Cost Breakdown by Room:")
        for room_id, info in cost_breakdown.items():
            print(f"    {info['room_name']}: ${info['total_cost']:.2f} ({info['count']} classes)")
        
        print(f"\n  Courses Scheduled: {len(result.assignments)}/{len(result.courses)}")
        
        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(result)
        
        save_schedule_to_file(result)
    else:
        print("\n[FAIL] Could not optimize for cost")

# ============================================================================
# MODE 5: MINIMIZE WALKING DISTANCE (A*)
# ============================================================================
def minimize_walking(data):
    """Reduce student walking between classes using A*"""
    print("\n" + "=" * 70)
    print("MINIMIZE WALKING DISTANCE")
    print("=" * 70)
    print("Optimizing schedule to reduce student walking...")
    
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    astar_solver = a_star(initial_schedule)
    start_time = time.time()
    result = astar_solver.find_path()
    elapsed = time.time() - start_time
    
    if result:
        walking_score = result.calculate_walking_distance()
        transitions = result.get_building_transitions()
        
        print(f"\n[OK] Schedule optimized in {elapsed:.2f} seconds")
        print(f"\nWalking Distance Metrics:")
        print(f"  Total Distance Score: {walking_score} meters")
        print(f"  Building Transitions: {sum(len(t) for t in transitions.values())}")
        
        if transitions:
            print(f"\n  Transitions by Day:")
            for day, trans in transitions.items():
                print(f"    {day.capitalize()}: {len(trans)} transitions")
        else:
            print(f"\n  [OK] No building transitions - all classes in same building!")
        
        print(f"\n  Courses Scheduled: {len(result.assignments)}/{len(result.courses)}")
        
        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(result)
        
        save_schedule_to_file(result)
    else:
        print("\n[FAIL] Could not optimize for walking distance")

# ============================================================================
# MODE 6: IMPROVE EXISTING SCHEDULE (HILL CLIMBING)
# ============================================================================
def improve_schedule(data):
    """Incrementally improve an existing schedule using Hill Climbing"""
    print("\n" + "=" * 70)
    print("IMPROVE EXISTING SCHEDULE")
    print("=" * 70)
    
    print("\nGenerating baseline schedule with CSP...")
    initial = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    csp_solver = csp(initial)
    previous = csp_solver.solve()
    
    if previous:
        print(f"  Baseline Fitness: {previous.calculate_fitness():.2f}")
        
        print("\nImproving schedule with Hill Climbing...")
        hc_solver = hill_climbing(previous)
        start_time = time.time()
        result = hc_solver.optimize()
        elapsed = time.time() - start_time
        
        if result:
            comparison = result.compare_to(previous)
            
            print(f"\n[OK] Schedule improved in {elapsed:.2f} seconds")
            print(f"\nImprovements:")
            print(f"  Fitness: {previous.calculate_fitness():.2f} -> {result.calculate_fitness():.2f}")
            print(f"  Change: {comparison['fitness_change']:+.2f}")
            print(f"  Assignments Changed: {comparison['assignments_changed']}")
            
            if comparison['improvements']:
                print(f"\n  Details:")
                for improvement in comparison['improvements']:
                    print(f"    - {improvement}")
            
            print("\n" + "=" * 70)
            print("IMPROVED SCHEDULE")
            print("=" * 70)
            print(result)
            
            save_schedule_to_file(result)
        else:
            print("\n[FAIL] Could not improve schedule")
    else:
        print("\n[FAIL] Could not generate baseline schedule")

# ============================================================================
# MODE 7: LARGE DATASET SCHEDULING (ITERATIVE DEEPENING)
# ============================================================================
def large_dataset_schedule(data):
    """Handle large scheduling problems efficiently using Iterative Deepening"""
    print("\n" + "=" * 70)
    print("LARGE DATASET SCHEDULING")
    print("=" * 70)
    
    num_courses = len(data["courses"])
    print(f"\nScheduling {num_courses} courses with memory-efficient algorithm...")
    
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    start_time = time.time()
    result = iterative_deepening(initial_schedule, max_depth=10)
    elapsed = time.time() - start_time
    
    if result:
        print(f"\n[OK] Schedule generated in {elapsed:.2f} seconds")
        print(f"\nPerformance Metrics:")
        print(f"  Courses Scheduled: {len(result.assignments)}/{num_courses}")
        print(f"  Memory Efficient: Yes")
        print(f"  Suitable for Large Datasets: Yes")
        
        print("\n" + "=" * 70)
        print("SCHEDULE")
        print("=" * 70)
        print(result)
        
        save_schedule_to_file(result)
    else:
        print("\n[FAIL] Could not generate schedule")

# ============================================================================
# MAIN FUNCTION
# ============================================================================
def main():
    """Main function with specialized scheduling modes"""
    print("\n" + "=" * 70)
    print("UNIVERSITY COURSE SCHEDULING SYSTEM")
    print("=" * 70)
    
    # Automatically load university data
    print("\nLoading university data...")
    try:
        data = load_from_json_file("university_data.json")
        print(f"[OK] Loaded {len(data['courses'])} courses, {len(data['rooms'])} rooms, {len(data['professors'])} professors")
    except FileNotFoundError:
        print("\n[FAIL] Error: university_data.json not found!")
        print("   Please ensure the file exists in the project directory.")
        return
    except Exception as e:
        print(f"\n[FAIL] Error loading data: {e}")
        return
    
    # Main loop - keep running until user exits
    while True:
        print("\n" + "=" * 70)
        print("SCHEDULING MODE")
        print("=" * 70)
        print("What would you like to do?\n")
        print("1. Quick Schedule")
        print("   -> Get any valid schedule fast")
        print("   -> Best for: Initial scheduling, testing\n")
        
        print("2. Urgent Scheduling")
        print("   -> Emergency scheduling, fastest possible")
        print("   -> Best for: Last-minute changes, room unavailable\n")
        
        print("3. Optimize Preferences")
        print("   -> Best quality schedule considering preferences")
        print("   -> Best for: Maximizing professor/student satisfaction\n")
        
        print("4. Minimize Costs")
        print("   -> Budget-conscious scheduling")
        print("   -> Best for: Cost reduction, budget constraints\n")
        
        print("5. Minimize Walking Distance")
        print("   -> Reduce student walking between classes")
        print("   -> Best for: Large campus, student complaints\n")
        
        print("6. Improve Existing Schedule")
        print("   -> Refine and improve schedule quality")
        print("   -> Best for: Incremental improvements\n")
        
        print("7. Large Dataset Scheduling")
        print("   -> Memory-efficient scheduling")
        print("   -> Best for: Any dataset size\n")
        
        print("x. Exit")
        
        choice = input("\nEnter choice (1-7 or x to exit): ").strip().lower()
        
        if choice == "x":
            print("\n" + "=" * 70)
            print("Thank you for using the University Course Scheduling System!")
            print("=" * 70)
            break
        elif choice == "1":
            quick_schedule(data)
        elif choice == "2":
            urgent_schedule(data)
        elif choice == "3":
            optimize_preferences(data)
        elif choice == "4":
            minimize_costs(data)
        elif choice == "5":
            minimize_walking(data)
        elif choice == "6":
            improve_schedule(data)
        elif choice == "7":
            large_dataset_schedule(data)
        else:
            print("\n  [FAIL] Invalid choice. Please enter 1-7 or x")

if __name__ == "__main__":
    main()