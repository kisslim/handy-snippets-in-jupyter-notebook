from collections import defaultdict, OrderedDict
from numbers import Real

def find_connected_components(adj_table):
    """
    Find connected components in a graph represented as an adjacency table
    adj_table: dict where keys are nodes and values are lists of neighbors
    """
    visited = set()
    components = []
    
    def dfs(node, component):
        visited.add(node)
        component.append(node)
        for neighbor in adj_table.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, component)
    
    for node in adj_table:
        if node not in visited:
            component = []
            dfs(node, component)
            yield component

def create_graph_max_degree_first_then_min_weight_first(
    nodes, 
    edge_index_tuples, 
    nodes_weight_func
):
    edge_set = {(y,x) for x,y in edge_index_tuples}
    edge_set.update(edge_index_tuples)
    graph = defaultdict(set)
    for x,y in edge_set:
        graph[x].add(y)
    graph_degrees = {x:len(y) for x,y in graph.items()}
    node_indexes = list(graph.keys())
    node_indexes.sort(key=lambda i: (-graph_degrees[i], nodes_weight_func(nodes[i])))
    node_index_rank = {x:i for i,x in enumerate(node_indexes)}
    result = OrderedDict()
    for i in node_indexes:
        result[i] = list(sorted(graph[i], key=lambda x: node_index_rank[x]))
    return result

def delete_node(graph, node):
    """Return a new graph with the specified node deleted"""
    # Create a new graph without the node
    new_graph = OrderedDict()
    
    for current_node, neighbors in graph.items():
        if current_node == node:
            continue  # Skip the node to be deleted
        
        # Create new neighbor list excluding the deleted node
        new_neighbors = [neighbor for neighbor in neighbors if neighbor != node]
        if new_neighbors:
            new_graph[current_node] = new_neighbors
    
    return new_graph

def constant(x):
    return 1

class MinimalVertexCoverSearcher:
    """
    search minimal vertex cover progressively. yield solutions while trying to minimize tuple (count, weight_sum). 
    ensure each solution is strictly smaller to previous yielded one.
    prune search tree when possible. 
    """
    def init(self):
        self.current_min_weight_sum : Real = float('inf')
        self.current_min_count : Real = float('inf')
        self.current_solution = None
        self.original_nodes = None
        self.original_graph = None
        self.search_order = None
        self.nodes_weight_func = constant
    
    def __init__(self, quiet=False):
        self.init()
        self.quiet = quiet

    def search_streamed(self, nodes, edges: Iterable[Tuple[int, int]], nodes_weight_func = constant):
        self.init()
        self.original_nodes = nodes
        self.original_graph = create_graph_max_degree_first_then_min_weight_first(nodes, edges, nodes_weight_func)
        self.search_order = list(self.original_graph)#{x:i for i,x in enumerate(self.original_graph))
        if not self.quiet:
            assert len(self.original_graph) == len(nodes), "you must include all nodes in the edge. otherwise, it is impossible to do vertex cover. "
            components = find_connected_components(adj_table=self.original_graph)
            print("component 1", next(components)) # TODO: remove debugging print
            try:
                print("component 2", next(components)) # TODO: remove debugging print
                raise ValueError("multiple connected components detected. You may want to split them using find_connected_components and run search individially. ")
            except StopIteration:
                pass # should not have second components in the graph
        self.nodes_weight_func = nodes_weight_func
        yield from self._search_streamed(0, [], self.original_graph)
    
    def _search_streamed(self, current_decision_index, selected_solution, current_graph):
        # print("current searching status", locals()) # TODO: remove debugging code
        current_count = len(selected_solution)  
        current_sum = sum(self.nodes_weight_func(self.original_nodes[i]) for i in selected_solution) 
        
        if current_count > self.current_min_count: 
            # print("(partial) solution", selected_solution, f"use {current_count} more than", self.current_min_count, "nodes")
            # not optimal even if we choose not to pick at later decisions
            return

        if current_count == self.current_min_count and current_sum >= self.current_min_weight_sum: 
            # print("(partial) solution", selected_solution, f"use {current_sum} more than", self.current_min_weight_sum)
            # not optimal even if we choose not to pick at later decisions
            return
        
        if len(current_graph) == 0:
            # we got a solution
            yield selected_solution, current_count, current_sum
            # yield first so at that time we can compare between previous solution and current solution conveniently
            self.current_min_weight_sum = current_sum
            self.current_min_count = current_count
            self.current_solution = selected_solution
            return
        
        if current_decision_index >= len(self.original_graph):  # self.original_graph might be None, but it is a private method. it is protected by create_graph_max_degree_first_then_min_weight_first which always returns a result
            # we can't find a solution, all index used.
            return
        picked_node = self.search_order[current_decision_index]
        if picked_node in current_graph: # try delete first to get (greedy) solution quickly. pruning happens inside
            # print(f"decide to delete {current_decision_index}th node",picked_node) # TODO: remove debugging code
            yield from self._search_streamed(current_decision_index + 1, selected_solution + [picked_node], delete_node(current_graph, picked_node))
        
        yield from self._search_streamed(current_decision_index + 1, selected_solution, current_graph)
