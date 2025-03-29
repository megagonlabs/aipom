from collections import defaultdict

def get_unique_vertices(edges):
    vertices = set()
    for u, v in edges:
        vertices.add(u)
        vertices.add(v)
    return vertices

def add_edges(edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
    return graph

def dfs(graph, v, visited, rec_stack):
    visited[v] = True
    rec_stack[v] = True
    for neighbor in graph[v]:
        if not visited[neighbor]:
            if dfs(graph, neighbor, visited, rec_stack):
                return True
        elif rec_stack[neighbor]:
            return True
    rec_stack[v] = False
    return False

def validate_dag(edges):
    '''
    Returns True if graph is a valid DAG, False otherwise. 
    '''
    graph = add_edges(edges)
    V = get_unique_vertices(edges)
    visited = {node: False for node in V}
    rec_stack = {node: False for node in V}
    for node in V:
        if not visited[node]:
            if dfs(graph, node, visited, rec_stack):
                return False
    return True

def plan_adherence(llm_plan, dag_plan):
    '''
    Check if the converted DAG plan aligns with the plan outputted by the LLM. Return True if aligned, False otherwise.
    '''
    llm_plan_edges = sorted([(x[0], x[1]) for x in llm_plan["edges"]])
    dag_plan_edges = sorted(dag_plan.edges(data=False))
    if llm_plan_edges == dag_plan_edges:
        return True
    return False
