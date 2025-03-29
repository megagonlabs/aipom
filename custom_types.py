from typing import Any, Literal, Union

from pydantic import BaseModel
from typing_extensions import TypedDict

from utils import InteractionType, MsgType, Status

###########################
# Chat message data type #
###########################

# class LLMMessage(BaseModel):
#     role: Literal["system", "assistant", "user"]
#     content: str

class BaseMessage(BaseModel):
    content: str
    timestamp: int

class UserMessage(BaseMessage):
    id: int | None = None
    role: Literal["user"]

class SystemMessage(BaseMessage):
    id: int | None = None
    role: Literal["system", "assistant"]
    response_to: int | None  # msg id or interaction id

Message = Union[UserMessage, SystemMessage]

################
# UI data type #
################

NodeInputVars = list[tuple[str, Any]]

class XYPosition(TypedDict):
    x: float
    y: float

class UINodeData(BaseModel):
    id: int | None = None
    task: str
    input: NodeInputVars = []
    output: list[str] = []
    agent: str  # agent_name
    params: dict = {}
    exec: dict[str, Any] | None = None
    plan_status: Literal["PLANNED", "MODIFIED"] = "PLANNED"
    exec_status: Literal["NONE", "MODIFIED", "EXECUTED"] = "NONE"
    # status: Literal["PLANNED", "PROCESSING", "TRIGGERED", "STARTED", "FINISHED"] = "PLANNED"

class UINode(BaseModel):
    id: str
    data: UINodeData
    position: XYPosition | None = None
    type: str | None = None

class UIEdgeData(BaseModel):
    src_node: int
    dest_node: int
    src_output: str
    dest_input: str
    plan_status: Literal["UNMODIFIED", "MODIFIED"] = "UNMODIFIED"

class UIEdge(BaseModel):
    id: str
    source: str
    target: str
    data: UIEdgeData | None
    type: str | None = None

class UIPlan(BaseModel):
    id: str
    query: str
    timestamp: int
    nodes: list[UINode]
    edges: list[UIEdge]

#####################################
# frontend <> backend communication #
#####################################

# base communication data type
class BaseComm(BaseModel):
    type: MsgType
    data: dict[str, Any]
    class Config:
        arbitrary_types_allowed = True

# front -> back
class ConnectionData(BaseModel):
    status: str
class ConnectionComm(BaseComm):
    type: MsgType.CONNECTION
    data: ConnectionData

# front -> back
class InteractionData(BaseModel):
    id: int | None = None
    interaction: InteractionType
    n: int | None
    n_attr: dict | None
    n_exec: Any
    n_exec_attr: str
    n_exec_attr_val: Any
    e_s: str | int | None
    e_t: str | int | None
    e_attr: dict | None
    edges: list[UIEdge] | None
    plan: UIPlan | None
    class Config:
        arbitrary_types_allowed = True
class InteractionComm(BaseComm):
    type: MsgType.INTERACTION
    data: InteractionData

# front -> back
class ExecuteData(BaseModel):
    mode: Literal["all", "single"]
    node_id: str | int | None
class ExecuteComm(BaseComm):
    type: MsgType.EXECUTE
    data: ExecuteData

# front -> back
class ResetComm(BaseComm):
    type: MsgType.RESET

# front <-> back
class ChatDataUser(BaseModel):
    user_message: UserMessage
class ChatDataSystem(BaseModel):
    system_response: SystemMessage
    chat_history: list[Message] | None
class ChatComm(BaseComm):
    type: MsgType.CHAT
    data: ChatDataUser | ChatDataSystem

# back -> front
class PlanData(BaseModel):
    plan: UIPlan
class PlanComm(BaseComm):
    type: MsgType.PLAN
    data: PlanData

# back -> front
class StatusData(BaseModel):
    action: str  # revisit
    status: Status
    message: str | None
    class Config:
        arbitrary_types_allowed = True
class StatusComm(BaseComm):
    type: MsgType.STATUS
    data: StatusData

#####################
# planner data type #
#####################

class Node(BaseModel):
    id: int
    name: str
    task: str
    # input: Optional[Dict[str, Optional[str]]]  # Removed default value
    # output: Optional[Dict[str, Optional[str]]]  # Removed default value
    input: list[list[str | None]]
    output: list[str]

class Edge(BaseModel):
    src_node: int
    dest_node: int
    # input: Optional[Dict[str, Optional[str]]]  # Removed default value
    # output: Optional[Dict[str, Optional[str]]]  # Removed default value
    src_output: str
    dest_input: str

class LLMPlan(BaseModel):
    nodes: list[Node]
    edges: list[Edge]


# class LLMPlanEdge(BaseModel):
#     id: str | int
#     name: str
#     input: list[str]
#     output: list[str]

# class LLMPlan(BaseModel):
#     query: str
#     nodes: list[LLMPlanNode]
#     edges: list[list[int]]

class LLMPlanWithMetadata(LLMPlan):
    id: str
    timestamp: int

######################
# Exec & Interaction #
######################

class ExecuteOption(BaseModel):
    mode: Literal["all", "propagate", "single"]
    node_id: int | None = None

class Action(BaseModel):
    action: Literal[0, 1, 2, 3, 4, 5]
    # action_category: str
    user_query: str | None = None
    plan_feedback: str | None = None
    execute: ExecuteOption | None = None
    # timestamp: int | None = None

action_schema = {
    "name": "next_action",
    "description": "Identify an action to perform next",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "integer",
                "description": "action id",
                "enum": [0, 1, 2, 3],
            },
            # "action_category": {
            #     "type": "string",
            #     "description": "action category id",
            # },
            "user_query": {
                "type": ["string", "null"],
                "description": "User query",
            },
            "plan_feedback": {
                "type": ["string", "null"],
                "description": "User's feedback on the current plan",
            },
            "execute": {
                "type": ["object", "null"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Execution mode",
                        "enum": ["all", "propagate", "single"],
                    },
                    "node_id": {
                        "type": ["integer", "null"],
                        "description": "ID of a node to start execution",
                    },
                },
                "required": ["mode", "node_id"],
                "additionalProperties": False,
            },
        },
        "required": [
            "action",
            # "action_category",
            "user_query",
            "plan_feedback",
            "execute",
        ],
        "additionalProperties": False,
    },
}

# action_response_schema = {
#     "name": "next_action",
#     "description": "Identify an action to perform next",
#     "strict": True,
#     "schema": {
#         "type": "object",
#         "properties": {
#             "action": {
#                 "type": "integer",
#                 "description": "action id",
#                 "enum": [1, 2, 3],
#             },
#             "action_category": {
#                 "type": "string",
#                 "description": "action category id",
#             },
#             "user_query": {
#                 "type": ["string", "null"],
#                 "description": "User query",
#             },
#             "plan_feedback": {
#                 "type": ["string", "null"],
#                 "description": "User's feedback on the current plan",
#             },
#             "execute": {
#                 "anyOf": [
#                     {
#                         "type": "integer",
#                         "description": "A specific step to execute",
#                     },
#                     {
#                         "type": "string",
#                         "description": "Which steps to execute",
#                     },
#                     {
#                         "type": "null",
#                     },
#                 ]
#             },
#         },
#         "required": [
#             "action",
#             "action_category",
#             "user_query",
#             "plan_feedback",
#             "execute",
#         ],
#         "additionalProperties": False,
#     },
# }
