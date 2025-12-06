import config
from models import schedule
from algorithms.dfs import dfs_schedule

def iterative_deepening(initial_schedule, max_depth=None):
    """Iterative Deepening Depth-First Search"""
    if max_depth is None:
        max_depth = config.ALGORITHM_CONFIG['iterative_deepening']['max_depth']
    
    depth_increment = config.ALGORITHM_CONFIG['iterative_deepening']['depth_increment']
    
    print("Starting Iterative Deepening...")
    
    for depth in range(1, max_depth + 1, depth_increment):
        print(f"\nTrying depth limit: {depth}")
        
        result = dfs_schedule(initial_schedule, max_depth=depth)
        if result:
            print(f"Found solution at depth {depth}")
            return result
    
    print(" Iterative Deepening could not find solution")
    return None