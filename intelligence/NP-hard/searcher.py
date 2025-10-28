"""

I want python types for progressive NP-hard problem searcher/solver. 
the base abstract class provides utilities and remains a core function for subclass to implement: 
    search_stream(problem: `Problem`) which is a generator yields either `Progress` or `Solution`. 
    we require that `Solution` is always comparable (i.e., supports <, <=, >, >=).
    the generator should always yield verifiable and better solution than before.
    
the data format is:

{-# LANGUAGE TypeFamilies #-}
class Problem a where
    type Progress a :: *
    type Solution a :: Ord
    describe :: a -> String
    merge_progress :: a -> Progress a -> a
    get_current_solution :: a -> Maybe (Solution a)
    verify :: a -> Solution a -> Bool

"""

from typing import TypeVar, Generic, Optional, Iterator, Union
from abc import ABC, abstractmethod

# Type variables for the problem domain
P = TypeVar('P', bound='Problem')  # Problem type
Progress = TypeVar('Progress')      # Progress type
Solution = TypeVar('Solution')      # Solution type


class Problem(ABC, Generic[P, Progress, Solution]):
    """Abstract base class representing an NP-hard problem."""
    
    @abstractmethod
    def describe(self) -> str:
        """Return a description of the problem."""
        pass
    
    @abstractmethod
    def merge_progress(self: P, progress: Progress) -> P:
        """
        Merge progress information into the current problem state.
        
        Args:
            progress: Progress information to merge
            
        Returns:
            Updated problem instance
        """
        pass
    
    @abstractmethod
    def get_current_solution(self) -> Optional[Solution]:
        """
        Get the current best solution found so far.
        
        Returns:
            Current best solution or None if no solution found yet
        """
        pass
    
    @abstractmethod
    def verify(self, solution: Solution) -> bool:
        """
        Verify if a solution is valid for this problem.
        
        Args:
            solution: Solution to verify
            
        Returns:
            True if the solution is valid
        """
        pass


class Solver(ABC, Generic[P, Progress, Solution]):
    """Abstract base class for progressive problem solvers."""
    
    @abstractmethod
    def search_stream(self, problem: P) -> Iterator[Union[Progress, Solution]]:
        """
        Generator that yields either progress updates or solutions.
        
        Args:
            problem: The problem to solve
            
        Yields:
            Either Progress updates or Solution objects
        """
        pass
    
    # Utility methods that subclasses can use
    def log_progress(self, progress: Progress) -> None:
        """Utility method to log progress updates."""
        print(f"Progress: {progress}")
    
    def log_solution(self, solution: Solution) -> None:
        """Utility method to log solutions."""
        print(f"Solution found: {solution}")


# Example concrete implementation types
class ExampleProgress:
    """Example progress type for demonstration."""
    def __init__(self, nodes_explored: int, best_bound: float):
        self.nodes_explored = nodes_explored
        self.best_bound = best_bound
    
    def __str__(self) -> str:
        return f"Nodes: {self.nodes_explored}, Bound: {self.best_bound}"


class ExampleSolution:
    """Example solution type for demonstration."""
    def __init__(self, value: int, assignment: list[int]):
        self.value = value
        self.assignment = assignment
    
    def __str__(self) -> str:
        return f"Value: {self.value}, Assignment: {self.assignment}"


class ExampleProblem(Problem['ExampleProblem', ExampleProgress, ExampleSolution]):
    """Example concrete problem implementation."""
    
    def __init__(self, data: list[int], current_progress: Optional[ExampleProgress] = None):
        self.data = data
        self.current_progress = current_progress
        self.best_solution: Optional[ExampleSolution] = None
    
    def describe(self) -> str:
        return f"Example problem with data: {self.data}"
    
    def merge_progress(self, progress: ExampleProgress) -> 'ExampleProblem':
        # Create a new instance with merged progress
        return ExampleProblem(self.data, progress)
    
    def get_current_solution(self) -> Optional[ExampleSolution]:
        return self.best_solution
    
    def verify(self, solution: ExampleSolution) -> bool:
        # Simple verification logic
        return (solution.value is not None and 
                len(solution.assignment) == len(self.data))


class ExampleSolver(Solver[ExampleProblem, ExampleProgress, ExampleSolution]):
    """Example concrete solver implementation."""
    
    def search_stream(self, problem: ExampleProblem) -> Iterator[Union[ExampleProgress, ExampleSolution]]:
        # Example implementation that yields progress and solutions
        yield ExampleProgress(0, 0.0)
        
        # Simulate some computation
        for i in range(1, 10):
            yield ExampleProgress(i * 100, i * 0.1)
            
            # Occasionally yield a solution
            if i % 3 == 0:
                solution = ExampleSolution(i, list(range(len(problem.data))))
                yield solution
        
        # Final solution
        final_solution = ExampleSolution(42, [1, 2, 3])
        yield final_solution


# Usage example
def solve_problem(problem: Problem[P, Progress, Solution], 
                 solver: Solver[P, Progress, Solution]) -> Optional[Solution]:
    """
    Solve a problem using a solver and return the best solution.
    
    Args:
        problem: The problem to solve
        solver: The solver to use
        
    Returns:
        Best solution found, or None if no solution found
    """
    best_solution: Optional[Solution] = None
    
    for result in solver.search_stream(problem):
        if isinstance(result, Problem):  # type: ignore
            # This would be progress in your actual implementation
            progress: Progress = result  # type: ignore
            print(f"Progress update: {progress}")
        else:
            # This is a solution
            solution: Solution = result  # type: ignore
            print(f"Found solution: {solution}")
            if best_solution is None or self._is_better(solution, best_solution):  # type: ignore
                best_solution = solution
    
    return best_solution

# For the comparison method, you'd need to add it to your Problem class
def _is_better(self, new_solution: Solution, current_best: Solution) -> bool:
    """Compare two solutions to determine which is better."""
    # Implementation depends on whether it's a minimization or maximization problem
    # This should be implemented in concrete problem classes
    pass