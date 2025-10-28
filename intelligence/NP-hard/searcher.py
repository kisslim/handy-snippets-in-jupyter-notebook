"""

I want python types for progressive NP-hard problem searcher/solver. 
the base abstract class provides utilities and remains a core function for subclass to implement: 
    search_stream(problem: `Problem`) which is a generator yields either `Progress` or `Solution`. 
    
the data format is:

{-# LANGUAGE TypeFamilies #-}
class Problem a where
    type Progress a :: *
    type Solution a :: *
    describe :: a -> String
    merge_progress :: a -> Progress a -> a
    get_current_solution :: a -> Maybe (Solution a)
    verify :: a -> Solution a -> Bool

"""