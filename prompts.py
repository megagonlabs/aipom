#################
# intent prompt #
#################

INTENT_DETECTION = '''
Given a user message, state the intent of the action needed. 
Intent can either be:

"plan": on an initial user query, the action needed is to generate plan
"refine": if user provides feedback to a plan
"execute": if user explicitly states desire to execute a plan

User query: 
{user_message}

Your answer should only be plan or replan or execute. No additional commentary. 
'''

INTENT_SYSTEM_PROMPT = """\
You are a natural language interface for a multi-agent system. This system creates a plan to answer a user query and executes it using AI agents. Your task is to chat with the user, decide the system's next action, and communicate the system's output to the user.

From a user's utterance, you need to infer the user's intention and choose one of the following actions. If the user seeks an answer to a query, describe the query without missing detail. If the user wants to modify the current plan, summarize the user's feedback in a clear sentence.

ACTION ID : ACTION
0: User query is not specified.
1: Initialize or update user query
2: Provide feedback on the current plan (user query is not changed)
3: Execute a specific step, from a specific step, or all steps

Your response should follow this JSON format:
{{
    'action': <action id>,
    'user_query': <query> or null,
    'plan_feedback': <plan feedback> or null,
    'execute': {{ 'mode': 'single' or 'all', 'node_id': <node id> or null }}
}}

<examples>
User: hi
action = 0
User: which companies hire data scientist in mountain view
action=1, user_query='which companies hire data scientist in mountain view'
User: simpler plan
action=2, plan_feedback='make a simpler plan'
User: how about in sunnyvale
action=1, user_query='which companies hire data scientist in sunnyvale'
User: remove step 3 in the plan
action=2, plan_feedback='remove step 3'
User: what are the average salary of those companies?
action=1, user_query='average salary of companies hiring data scientists in sunnyvale'
User: 1+2+3
action=1, user_query='calculate 1+2+3'
</examples>
"""

###################
# response prompt #
###################

RESPONSE_MESSAGE_PLAN = '''
Generate a very short (max 1-2 line) response to a user query to generate a plan.
The response should simply provide a high level response of what the plan does, and minor details such as number of steps. 

User Query: {query}
Plan: {plan}
'''

RESPONSE_MESSAGE_EXECUTE = '''
Generate a very short (max 1-2 line) response to a user query to execute a plan or a single node.
The response should simply provide a high level response of the execution, and minor details such as final result. 

User Query: {query}
Plan: {plan}
'''

RESPONSE_MESSAGE_INTERACT = '''
Generate a very short (max 1-2 line) response to a user query to interact with a plan.
The response should simply provide a high level response of the plan which was interacted with and what change took place.

Interaction Type: {interaction}
Plan: {plan}
'''

RESPONSE_SYSTEM_PROMPT = """\
You are a natural language interface for a multi-agent system.
This system creates a plan to answer a user query and executes it using AI agents.
Your task is to explain the actions triggered by the user input and clearly communicate the system's output in a very short (max 1-2 line) response.
Do not mention anything else. Write down only plain text."""

# RESPONSE_PROMPT_PLAN = """\
# User input: New user query was [{user_query}].
# System action(s): Plan updated as:\n\n{plan}
# """

# RESPONSE_PROMPT_REFINE = """\
# User input: User feedback was [{plan_feedback}].
# System action(s): Plan updated as:\n\n{plan}
# """

# RESPONSE_PROMPT_EXECUTE = """\
# User input: User requested execution.
# System executed the plan.

# Result:\n\n{result}
# """

###############
# plan prompt #
###############

PLAN_SYSTEM_PROMPT = """\
You are a planner responsible for creating high-level plans to solve any tasks using a set of agents.
Your goal is to break down a given task into a sequence of subtasks that, when executed correctly by the appropriate agents, will lead to the correct solution.
A plan should have at least 2 steps.

For each step in the plan:
1. Describe the subtask the agent must perform.
2. Provide a brief, self-contained description of the expected inputs and outputs. Do not include any specific values or examples.
3. Generate an instruction prompt for the agent.

Represent your plan as a graph where each node corresponds to a step, and each edge represents a dependency between two steps i.e., a step's output is used as an input for a subsequent step.
If a node requires the output from a previous node as an input, ensure it is included in the edge list.
An input variable for a node represented is a tuple, where the first item is an input description, the second item is the value of the variable if it can be predetermined without executing the plan.
If is dependent upon preceding nodes, set null. DO NOT INFER THE VALUE. DO NOT EXECUTE THE STEPS.
The output should be structured in the following JSON format:
{{ 
    'nodes': <list of JSON nodes {{'id': <node id as integer>, 'name': <assigned agent name>, 'task': <instruction prompt>, 'input': <list of tuple (input var, its value)>, 'output': <list of outputs>}}>,
    'edges': <list of JSON edges {{'src_node': <source node id>, 'dest_node': <destination node id>, 'src_output': <output variable name>, 'dest_input': <input variable name>}}>
}}

eg. 
1. query: A raspberry bush has 6 clusters of 20 fruit each and 7 individual fruit scattered across the bush. How many raspberries are there in total?
plan:
"nodes": [
    {{
        "id": 0,
        "name": "identify_operands",
        "task": "Identify the number of clusters, fruits per cluster and number of individual fruits from the query",
        "input": [["query", "A raspberry bush has 6 clusters of 20 fruit each and 7 individual fruit scattered across the bush. How many raspberries are there in total?"]],
        "output": ["num_clusters", "fruits_per_cluster", "individual_fruits"]
    }},
    {{
        "id": 1,
        "name": "multiply",
        "task": "Calculate total number of fruits in all clusters by multiplying the number of clusters with the number of fruits per cluster",
        "input": [["num_clusters", null], ["fruits_per_cluster", null]]
        "output":["total_fruits_in_clusters"]
    }},
    {{
        "id": 2,
        "name": "add",
        "task": "Find the total number of raspberries by adding the total number of fruits in clusters with total number of individual fruits",
        "input": [["total_fruits_in_clusters", null], ["total_individual_fruits", null]]
        "output":["total_raspberries"]
    }}
],
"edges": [
    {{
        'src_node': 0,
        'src_output': 'num_clusters',
        'dest_node': 1,
        'dest_input': 'num_clusters'
    }},
    {{
        'src_node': 0,
        'src_output': 'fruits_per_cluster',
        'dest_node': 1 ,
        'dest_input': 'fruits_per_cluster'
    }},
    {{
        'src_node': 1,
        'src_output': 'total_fruits_in_clusters',
        'dest_node': 2 ,
        'dest_input': 'total_fruits_in_clusters'
    }},
    {{
        'src_node': 0,
        'src_output': 'individual_fruits',
        'dest_node': 2,
        'dest_input': 'total_individual_fruits'
    }},
]

2. query: Out of a total of 10 balls, 2 are red. The number of blue balls is twice the number of red balls. The remaining balls are green. What fraction of the total balls are green?
plan:
"nodes": [
    {{
        "id": 0,
        "name": "identify_operands",
        "task": "Identify the total number of balls, number of red balls, and blue multiplier from the following query",
        "input": [["query", "Out of a total of 10 balls, 2 are red. The number of blue balls is twice the number of red balls. The remaining balls are green. What fraction of the total balls are green?"]],
        "output": ["total_balls", "red_balls"]
    }},
    {{
        "id": 1,
        "name": "multiply",
        "task": "Calculate number of blue balls by multiplying the number of red balls by 2",
        "input": [["red_balls", null], ["multiplier", 2]]
        "output": ["blue_balls"]
    }},,
    {{
        "id": 2,
        "name": "subtract",
        "task": "Calculate number of green balls by subtracting the number of red balls and blue balls from total balls",
        "input": [["total_balls", null], ["red_balls", null], ["blue_balls", null]]
        "output": ["green_balls"]
    }},
    {{
        "id": 3,
        "name": "divide",
        "task": "Calculate fraction of green balls by dividing the number of green balls by total number of balls",
        "input": [["green_balls", null], ["total_balls", null]],
        "output": ["fraction_green_balls"]
    }}
]
"edges": [
    {{
        'src_node': 0,
        'src_output': 'red_balls'
        'dest_node': 1 ,
        'dest_input': 'red_balls'
    }},
    {{
        'src_node': 0,
        'src_output': 'total_balls',
        'dest_node': 2,
        'dest_input': 'total_balls'
    }},
    {{
        'src_node': 0,
        'src_output': 'red_balls'
        'dest_node': 2 ,
        'dest_input': 'red_balls'
    }},
    {{
        'src_node': 1,
        'src_output': 'blue_balls',
        'dest_node': 2,
        'dest_input': 'blue_balls'
    }},
    {{
        'src_node': 0,
        'src_output': 'total_balls',
        'dest_node': 3,
        'dest_input': 'total_balls'
    }},
    {{
        'src_node': 2,
        'src_output': 'green_balls',
        'dest_node': 3,
        'dest_input': 'green_balls'
    }}
]

Here are the available agents:
```
{agent_registry}
```

For identify_operands, ensure you repeat the query in the task. Sometimes, the query may require a multiplier eg. "..twice of", divisor eg. "divide by x", percentage, in a later task. Ensure all such operations are also captured in identify_operands.
There may be multiple inputs from one node to another. In that case, ensure you define separate edges from one node to the other.
For some agents, ensure that input order is correct, e.g., when calculating profit, revenue - cost is different from cost - revenue. so input should be [revenue, cost] order.
"""

# PLAN_SYSTEM_PROMPT_backup = """\
# You are a planner responsible for creating high-level plans to solve any tasks using a set of agents.
# Your goal is to break down a given task into a sequence of subtasks that, when executed correctly by the appropriate agents, will lead to the correct solution.
# A plan should have at least 2 steps.

# For each step in the plan:
# 1. Describe the subtask the agent must perform.
# 2. Provide a brief, self-contained description of the expected inputs and outputs. Do not include any specific values or examples.
# 3. Generate an instruction prompt for the agent.

# Represent your plan as a graph where each node corresponds to a step, and each edge represents a dependency between two steps i.e., a step's output is used as an input for a subsequent step.
# If a node requires the output from a previous node as an input, ensure it is included in the edge list.
# The output should be structured in the following JSON format:
# {{ 
#     'nodes': <list of JSON nodes {{'id': <node id as integer>, 'name': <assigned agent name>, 'task': <instruction prompt>, 'input': <list of inputs>, 'output': <list of outputs>}}>,
#     'edges': <list of JSON edges {{'src_node': <source node id>, 'dest_node': <destination node id>, 'src_output': <output variable name>, 'dest_input': <input variable name>}}>
# }}

# eg. 
# 1. query: A raspberry bush has 6 clusters of 20 fruit each and 7 individual fruit scattered across the bush. How many raspberries are there in total?
# plan:
# "nodes": [
#     {{
#         "id": 0,
#         "name": "identify_operands",
#         "task": "Identify the number of clusters, fruits per cluster and number of individual fruits from the following query: A raspberry bush has 6 clusters of 20 fruit each and 7 individual fruit scattered across the bush. How many raspberries are there in total?",
#         "input": [],
#         "output": ["num_clusters", "fruits_per_cluster", "individual_fruits"]
#     }},
#     {{
#         "id": 1,
#         "name": "multiply",
#         "task": "Calculate total number of fruits in all clusters by multiplying the number of clusters with the number of fruits per cluster",
#         "input": ["num_clusters", "fruits_per_cluster"]
#         "output":["total_fruits_in_clusters"]
#     }},
#     {{
#         "id": 2,
#         "name": "add",
#         "task": "Find the total number of raspberries by adding the total number of fruits in clusters with total number of individual fruits",
#         "input": ["total_fruits_in_clusters", "total_individual_fruits"]
#         "output":["total_raspberries"]
#     }}
# ],
# "edges": [
#     {{
#         'src_node': 0,
#         'src_output': 'num_clusters',
#         'dest_node': 1,
#         'dest_input': 'num_clusters'
#     }},
#     {{
#         'src_node': 0,
#         'src_output': 'fruits_per_cluster',
#         'dest_node': 1 ,
#         'dest_input': 'fruits_per_cluster'
#     }},
#     {{
#         'src_node': 1,
#         'src_output': 'total_fruits_in_clusters',
#         'dest_node': 2 ,
#         'dest_input': 'total_fruits_in_clusters'
#     }},
#     {{
#         'src_node': 0,
#         'src_output': 'individual_fruits',
#         'dest_node': 2,
#         'dest_input': 'total_individual_fruits'
#     }},
# ]

# 2. query: Out of a total of 10 balls, 2 are red. The number of blue balls is twice the number of red balls. The remaining balls are green. What fraction of the total balls are green?
# plan:
# "nodes": [
#     {{
#         "id": 0,
#         "name": "identify_operands",
#         "task": "Identify the total number of balls, number of red balls, and blue multiplier from the following query: 2. query: Out of a total of 10 balls, 2 are red. The number of blue balls is twice the number of red balls. The remaining balls are green. What fraction of the total balls are green?",
#         "input": [],
#         "output": ["total_balls", "red_balls", "blue_to_red_multiplier"]
#     }},
#     {{
#         "id": 1,
#         "name": "multiply",
#         "task": "Calculate number of blue balls by multiplying the number of red balls with the multiplier",
#         "input": ["red_balls", "multiplier"]
#         "output": ["blue_balls"]
#     }},,
#     {{
#         "id": 2,
#         "name": "subtract",
#         "task": "Calculate number of green balls by subtracting the number of red balls and blue balls from total balls",
#         "input": ["total_balls", "red_balls", "blue_balls"]
#         "output": ["green_balls"]
#     }},
#     {{
#         "id": 3,
#         "name": "divide",
#         "task": "Calculate fraction of green balls by dividing the number of green balls by total number of balls",
#         "input": ["green_balls", "total_balls"],
#         "output": ["fraction_green_balls"]
#     }}
# ]
# "edges": [
#     {{
#         'src_node': 0,
#         'src_output': 'red_balls'
#         'dest_node': 1 ,
#         'dest_input': 'red_balls'
#     }},
#     {{
#         'src_node': 0,
#         'src_output': 'blue_to_red_multiplier',
#         'dest_node': 1,
#         'dest_input': 'multiplier'
#     }},
#     {{
#         'src_node': 0,
#         'src_output': 'total_balls',
#         'dest_node': 2,
#         'dest_input': 'total_balls'
#     }},
#     {{
#         'src_node': 0,
#         'src_output': 'red_balls'
#         'dest_node': 2 ,
#         'dest_input': 'red_balls'
#     }},
#     {{
#         'src_node': 1,
#         'src_output': 'blue_balls',
#         'dest_node': 2,
#         'dest_input': 'blue_balls'
#     }},
#     {{
#         'src_node': 0,
#         'src_output': 'total_balls',
#         'dest_node': 3,
#         'dest_input': 'total_balls'
#     }},
#     {{
#         'src_node': 2,
#         'src_output': 'green_balls',
#         'dest_node': 3,
#         'dest_input': 'green_balls'
#     }}
# ]

# Here are the available agents:
# ```
# {agent_registry}
# ```

# For identify_operands, ensure you repeat the query in the task. Sometimes, the query may require a multiplier eg. "..twice of", divisor eg. "divide by x", percentage, in a later task. Ensure all such operations are also captured in identify_operands.
# There may be multiple inputs from one node to another. In that case, ensure you define separate edges from one node to the other.
# For some agents, ensure that input order is correct, e.g., when calculating profit, revenue - cost is different from cost - revenue. so input should be [revenue, cost] order.
# """

PLAN_REFINE_PROMPT = """\
Given the original plan, refine it according to user feedback

Original Plan:
{prev_plan}

User Feedback:
{feedback}
"""

PLAN_FIX_PROMPT = '''
Given a query, an initial plan will be given to you. The initial plan may be incomplete or incorrect.
Your job is to complete or fix the plan. Stay as true to the initial plan as you can.

Query:
{query}

Intial Plan:
{plan}
'''