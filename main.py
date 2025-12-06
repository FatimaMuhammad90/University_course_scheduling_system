
"""
University Course Scheduling System - Main Entry Point
"""

import json
import time
from models import course, room, professor, schedule
from algorithms import csp, genetic, a_star, hill_climbing, bfs_schedule, dfs_schedule, iterative_deepening, ucs
import config

def load_sample_data():
    """Create sample data for demonstration"""
    print("Creating sample data...")
    
    # Create professors
    prof1 = professor(
        professor_id="prof001",
        name="Dr. Alice Smith",
        department="Computer Science",
        courses=["cs101", "cs201", "cs301"],
        max_hours=12,
        preferences={
            "preferred_days": ["monday", "wednesday", "friday"],
            "preferred_times": ["morning"],
        }
    )
    
    prof2 = professor(
        professor_id="prof002",
        name="Dr. Bob Johnson",
        department="Computer Science",
        courses=["cs101", "cs202"],
        max_hours=10,
        preferences={
            "preferred_days": ["tuesday", "thursday"],
            "preferred_times": ["afternoon"],
        }
    )
    
    # Create rooms
    room1 = room(
        room_id="room101",
        name="Science 101",
        capacity=80,
        room_type="lecture_hall",
        features=["projector", "whiteboard"],
        building="Science Building",
        cost_per_hour=15.0
    )
    
    room2 = room(
        room_id="room202",
        name="Science 202",
        capacity=60,
        room_type="lecture_hall",
        features=["projector", "whiteboard", "sound_system"],
        building="Science Building",
        cost_per_hour=20.0
    )
    
    room3 = room(
        room_id="lab1",
        name="Computer Lab 1",
        capacity=40,
        room_type="lab",
        features=["computers", "projector"],
        building="Engineering Building",
        cost_per_hour=25.0
    )
    
    # Create courses
    courses_list = [
        course(
            course_id="cs101",
            name="Introduction to Programming",
            department="Computer Science",
            credits=3,
            students=60,
            course_type="lecture",
            professors=["prof001", "prof002"],
            preferred_times=["morning"],
            required_rooms=["projector"]
        ),
        course(
            course_id="cs201",
            name="Data Structures",
            department="Computer Science",
            credits=4,
            students=45,
            course_type="lecture",
            professors=["prof001"],
            prerequisites=["cs101"],
            preferred_times=["morning", "afternoon"],
            required_rooms=["projector"]
        ),
        course(
            course_id="cs202",
            name="Algorithms",
            department="Computer Science",
            credits=4,
            students=35,
            course_type="lecture",
            professors=["prof002"],
            prerequisites=["cs201"],
            preferred_times=["afternoon"],
            required_rooms=["projector"]
        ),
        course(
            course_id="lab_cs101",
            name="Programming Lab",
            department="Computer Science",
            credits=1,
            students=20,
            course_type="lab",
            professors=["prof001", "prof002"],
            required_rooms=["computers"]
        )
    ]
    
    return {
        "courses": courses_list,
        "rooms": [room1, room2, room3],
        "professors": [prof1, prof2]
    }

def demonstrate_all_algorithms():
    """Run and compare all algorithms"""
    print("=" * 70)
    print("UNIVERSITY COURSE SCHEDULING SYSTEM")
    print("DEMONSTRATING ALL ALGORITHMS")
    print("=" * 70)
    
    # Load data
    data = load_sample_data()
    
    # Create initial empty schedule
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    print(f"\n📊 Problem Size:")
    print(f"  Courses: {len(initial_schedule.courses)}")
    print(f"  Rooms: {len(initial_schedule.rooms)}")
    print(f"  Professors: {len(initial_schedule.professors)}")
    print(f"  Time slots per day: {len(config.TIME_SLOTS)}")
    print(f"  Days: {len(config.DAYS)}")
    
    results = {}
    
    # 1. CSP Algorithm
    print("\n" + "=" * 70)
    print("1. CONSTRAINT SATISFACTION PROBLEM (CSP)")
    print("=" * 70)
    print("Purpose: Find any valid schedule satisfying all hard constraints")
    print("Method: Backtracking with MRV, Degree, LCV heuristics")
    print("Use case: Initial schedule generation")
    
    csp_solver = csp(initial_schedule)
    start_time = time.time()
    csp_result = csp_solver.solve()
    csp_time = time.time() - start_time
    
    if csp_result:
        results['CSP'] = {
            'schedule': csp_result,
            'time': csp_time,
            'fitness': csp_result.calculate_fitness(),
            'assignments': len(csp_result.assignments)
        }
    
    # 2. Genetic Algorithm
    print("\n" + "=" * 70)
    print("2. GENETIC ALGORITHM")
    print("=" * 70)
    print("Purpose: Find high-quality schedule through evolution")
    print("Method: Population-based search with crossover and mutation")
    print("Use case: Generating multiple good alternatives")
    
    ga_solver = genetic(csp_result if csp_result else initial_schedule)
    start_time = time.time()
    ga_result = ga_solver.evolve(generations=200)  # Smaller for demo
    ga_time = time.time() - start_time
    
    if ga_result:
        results['Genetic'] = {
            'schedule': ga_result,
            'time': ga_time,
            'fitness': ga_result.calculate_fitness(),
            'assignments': len(ga_result.assignments)
        }
    
    # 3. A* Search
    print("\n" + "=" * 70)
    print("3. A* SEARCH")
    print("=" * 70)
    print("Purpose: Find optimal schedule with heuristic guidance")
    print("Method: Informed search with heuristic function")
    print("Use case: When optimal solution is needed")
    
    astar_solver = a_star(initial_schedule)
    start_time = time.time()
    astar_result = astar_solver.find_path()
    astar_time = time.time() - start_time
    
    if astar_result:
        results['A*'] = {
            'schedule': astar_result,
            'time': astar_time,
            'fitness': astar_result.calculate_fitness(),
            'assignments': len(astar_result.assignments)
        }
    
    # 4. Hill Climbing
    print("\n" + "=" * 70)
    print("4. HILL CLIMBING")
    print("=" * 70)
    print("Purpose: Local optimization of existing schedule")
    print("Method: Local search with random restarts")
    print("Use case: Incremental improvements")
    
    hc_solver = hill_climbing(ga_result if ga_result else csp_result if csp_result else initial_schedule)
    start_time = time.time()
    hc_result = hc_solver.optimize()
    hc_time = time.time() - start_time
    
    if hc_result:
        results['Hill Climbing'] = {
            'schedule': hc_result,
            'time': hc_time,
            'fitness': hc_result.calculate_fitness(),
            'assignments': len(hc_result.assignments)
        }
    
    # 5. BFS
    print("\n" + "=" * 70)
    print("5. BREADTH-FIRST SEARCH (BFS)")
    print("=" * 70)
    print("Purpose: Guaranteed minimal-depth solution")
    print("Method: Level-by-level exploration")
    print("Use case: Emergency scheduling (minimal changes)")
    
    start_time = time.time()
    bfs_result = bfs_schedule(initial_schedule, max_depth=5)
    bfs_time = time.time() - start_time
    
    if bfs_result:
        results['BFS'] = {
            'schedule': bfs_result,
            'time': bfs_time,
            'fitness': bfs_result.calculate_fitness(),
            'assignments': len(bfs_result.assignments)
        }
    
    # 6. DFS
    print("\n" + "=" * 70)
    print("6. DEPTH-FIRST SEARCH (DFS)")
    print("=" * 70)
    print("Purpose: Memory-efficient exploration")
    print("Method: Depth-first exploration with backtracking")
    print("Use case: When memory is limited")
    
    start_time = time.time()
    dfs_result = dfs_schedule(initial_schedule, max_depth=5)
    dfs_time = time.time() - start_time
    
    if dfs_result:
        results['DFS'] = {
            'schedule': dfs_result,
            'time': dfs_time,
            'fitness': dfs_result.calculate_fitness(),
            'assignments': len(dfs_result.assignments)
        }
    
    # 7. Iterative Deepening
    print("\n" + "=" * 70)
    print("7. ITERATIVE DEEPENING")
    print("=" * 70)
    print("Purpose: Combines BFS completeness with DFS memory efficiency")
    print("Method: Repeated DFS with increasing depth limits")
    print("Use case: When unsure about solution depth")
    
    start_time = time.time()
    id_result = iterative_deepening(initial_schedule, max_depth=5)
    id_time = time.time() - start_time
    
    if id_result:
        results['Iterative Deepening'] = {
            'schedule': id_result,
            'time': id_time,
            'fitness': id_result.calculate_fitness(),
            'assignments': len(id_result.assignments)
        }
    
    # 8. Uniform Cost Search
    print("\n" + "=" * 70)
    print("8. UNIFORM COST SEARCH (UCS)")
    print("=" * 70)
    print("Purpose: Find minimum cost schedule")
    print("Method: Cost-based priority queue")
    print("Use case: Budget-constrained scheduling")
    
    ucs_solver = ucs(initial_schedule)
    start_time = time.time()
    ucs_result = ucs_solver.find_min_cost_schedule()
    ucs_time = time.time() - start_time
    
    if ucs_result:
        results['UCS'] = {
            'schedule': ucs_result,
            'time': ucs_time,
            'fitness': ucs_result.calculate_fitness(),
            'assignments': len(ucs_result.assignments)
        }
    
    # Display results comparison
    print("\n" + "=" * 70)
    print("RESULTS COMPARISON")
    print("=" * 70)
    
    if results:
        print(f"\n{'Algorithm':<25} {'Time (s)':<10} {'Fitness':<10} {'Assignments':<12} {'Valid':<8}")
        print("-" * 70)
        
        for algo, data in results.items():
            print(f"{algo:<25} {data['time']:<10.2f} {data['fitness']:<10.2f} "
                  f"{data['assignments']:<12} {data['schedule'].is_valid():<8}")
        
        # Find best schedule
        best_algo = max(results.items(), key=lambda x: x[1]['fitness'])
        print(f"\n🏆 BEST SCHEDULE: {best_algo[0]} (Fitness: {best_algo[1]['fitness']:.2f})")
        
        # Display best schedule
        print("\n" + "=" * 70)
        print("FINAL SCHEDULE")
        print("=" * 70)
        print(best_algo[1]['schedule'])
        
        # Save to file
        save_schedule_to_file(best_algo[1]['schedule'])
    else:
        print("\n❌ No algorithms produced a valid schedule")
    
    print("\n" + "=" * 70)
    print("ALGORITHM JUSTIFICATIONS")
    print("=" * 70)
    print("""
1. CSP: Perfect for initial constraint validation - ensures all hard constraints are met
2. Genetic Algorithm: Excellent for exploring solution space and generating alternatives
3. A*: Optimal when good heuristics are available (walking distance, preferences)
4. Hill Climbing: Efficient for local optimization of existing schedules
5. BFS: Guarantees minimal changes - ideal for emergency scenarios
6. DFS: Memory-efficient for exploring deep constraint chains
7. Iterative Deepening: Best of BFS and DFS - complete but memory-efficient
8. UCS: Essential for budget-conscious scheduling with cost optimization
    """)

def save_schedule_to_file(schedule_obj, filename="output/schedule.txt"):
    """Save schedule to file"""
    import os
    os.makedirs("output", exist_ok=True)
    
    with open(filename, "w") as f:
        f.write(str(schedule_obj))
    
    print(f"\n💾 Schedule saved to {filename}")

def emergency_scenario_demo():
    """Demonstrate emergency scenario handling"""
    print("\n" + "=" * 70)
    print("EMERGENCY SCENARIO DEMONSTRATION")
    print("=" * 70)
    print("Scenario: Room 'Science 101' becomes unavailable suddenly")
    
    # Create a schedule first
    data = load_sample_data()
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    # Create a simple schedule
    csp_solver = csp(initial_schedule)
    current_schedule = csp_solver.solve()
    
    if current_schedule:
        print("\nCurrent schedule (before emergency):")
        print(f"  Fitness: {current_schedule.calculate_fitness():.2f}")
        
        # Simulate room outage
        print("\n🚨 EMERGENCY: Room 'Science 101' is now unavailable!")
        
        # Remove assignments to that room
        emergency_schedule = current_schedule.copy()
        assignments_to_remove = []
        
        for assignment in emergency_schedule.assignments:
            if assignment['room'].room_id == "room101":
                assignments_to_remove.append(assignment)
        
        for assignment in assignments_to_remove:
            emergency_schedule.remove_assignment(assignment)
        
        print(f"  {len(assignments_to_remove)} courses need rescheduling")
        
        # Use BFS for minimal changes
        print("\nUsing BFS for minimal-change rescheduling...")
        start_time = time.time()
        new_schedule = bfs_schedule(emergency_schedule, max_depth=3)
        rescue_time = time.time() - start_time
        
        if new_schedule:
            print(f"  ✓ Rescheduled in {rescue_time:.2f} seconds")
            print(f"  New fitness: {new_schedule.calculate_fitness():.2f}")
            print(f"  Valid: {new_schedule.is_valid()}")
        else:
            print("  ✗ Could not reschedule with BFS")
            
            # Try DFS as backup
            print("\nTrying DFS as backup...")
            start_time = time.time()
            new_schedule = dfs_schedule(emergency_schedule, max_depth=5)
            rescue_time = time.time() - start_time
            
            if new_schedule:
                print(f"  ✓ Rescheduled with DFS in {rescue_time:.2f} seconds")

def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("UNIVERSITY COURSE SCHEDULING SYSTEM")
    print("=" * 70)
    print("\nSelect mode:")
    print("1. Run all algorithms comparison")
    print("2. Emergency scenario demonstration")
    print("3. Run specific algorithm")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demonstrate_all_algorithms()
    elif choice == "2":
        emergency_scenario_demo()
    elif choice == "3":
        run_specific_algorithm()
    else:
        print("Invalid choice. Running default comparison...")
        demonstrate_all_algorithms()

def run_specific_algorithm():
    """Run a specific algorithm"""
    print("\nAvailable algorithms:")
    print("1. CSP (Constraint Satisfaction)")
    print("2. Genetic Algorithm")
    print("3. A* Search")
    print("4. Hill Climbing")
    print("5. BFS")
    print("6. DFS")
    print("7. Iterative Deepening")
    print("8. Uniform Cost Search")
    
    choice = input("\nSelect algorithm (1-8): ").strip()
    
    data = load_sample_data()
    initial_schedule = schedule(
        courses=data["courses"],
        rooms=data["rooms"],
        professors=data["professors"]
    )
    
    start_time = time.time()
    
    if choice == "1":
        solver = csp(initial_schedule)
        result = solver.solve()
    elif choice == "2":
        solver = genetic(initial_schedule)
        result = solver.evolve(generations=100)
    elif choice == "3":
        solver = a_star(initial_schedule)
        result = solver.find_path()
    elif choice == "4":
        solver = hill_climbing(initial_schedule)
        result = solver.optimize()
    elif choice == "5":
        result = bfs_schedule(initial_schedule)
    elif choice == "6":
        result = dfs_schedule(initial_schedule)
    elif choice == "7":
        result = iterative_deepening(initial_schedule)
    elif choice == "8":
        solver = ucs(initial_schedule)
        result = solver.find_min_cost_schedule()
    else:
        print("Invalid choice")
        return
    
    elapsed = time.time() - start_time
    
    if result:
        print(f"\n✅ Algorithm completed in {elapsed:.2f} seconds")
        print(f"   Fitness: {result.calculate_fitness():.2f}")
        print(f"   Valid: {result.is_valid()}")
        print(f"   Assignments: {len(result.assignments)}/{len(initial_schedule.courses)}")
        print("\nSchedule:")
        print(result)
    else:
        print("❌ Algorithm failed to find solution")

if __name__ == "__main__":
    main()