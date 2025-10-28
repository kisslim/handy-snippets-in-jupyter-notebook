"""

I want python types for progressive NP-hard problem searcher/solver. 
the base abstract class provides utilities and remains a core function for subclass to implement: 
    search_stream(problem: `Problem`) which is a generator yields either `Progress` or `Solution`. 
    we require that `Solution` is always comparable (i.e., supports <, <=, >, >=).
    the generator should always yield verifiable and better (>=) solution than before.
    
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
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterator, Union, Optional
from typing_extensions import Protocol

# Type variables for the Problem type and its associated types
P = TypeVar('P', bound='Problem')  # Problem type
S = TypeVar('S', bound='Comparable')  # Solution type - must be comparable

# Protocol for comparable types (equivalent to Haskell's Ord)
class Comparable(Protocol):
    def __lt__(self, other: 'Comparable') -> bool: ...
    def __le__(self, other: 'Comparable') -> bool: ...
    def __gt__(self, other: 'Comparable') -> bool: ...
    def __ge__(self, other: 'Comparable') -> bool: ...

class Progress(ABC):
    """Base class for progress updates"""
    pass

class Problem(ABC, Generic[P, S]):
    """
    Abstract base class for NP-hard problems.
    
    Type Parameters:
        P: The specific Problem type (self-referential)
        S: The Solution type (must be Comparable)
    """
    
    @abstractmethod
    def describe(self) -> str:
        """Return a description of the problem instance."""
        pass
    
    @abstractmethod
    def merge_progress(self: P, progress: Progress) -> P:
        """
        Merge progress information into the problem state.
        
        Returns a new problem instance with the merged progress.
        """
        pass
    
    @abstractmethod
    def get_current_solution(self) -> Optional[S]:
        """Get the current best solution, if any."""
        pass
    
    @abstractmethod
    def verify(self, solution: S) -> bool:
        """Verify that a solution is valid for this problem."""
        pass

class Solver(ABC, Generic[P, S]):
    """
    Abstract base class for progressive NP-hard problem solvers.
    
    Type Parameters:
        P: The Problem type this solver works with
        S: The Solution type (must be Comparable)
    """
    
    @abstractmethod
    def search_stream(self, problem: P) -> Iterator[Union[Progress, S]]:
        """
        Generator that yields either Progress updates or Solutions.
        
        Solutions must be comparable and each yielded solution should be
        better than or equal to the previous one (>=).
        Solutions should always be verifiable.
        """
        pass
    
    # Utility methods can be added here for subclasses
    def _verify_solution(self, problem: P, solution: S) -> bool:
        """Utility method to verify a solution."""
        return problem.verify(solution)
    
    def _get_problem_description(self, problem: P) -> str:
        """Utility method to get problem description."""
        return problem.describe()
