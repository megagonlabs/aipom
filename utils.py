import json
import os
import time
import uuid
from graphlib import TopologicalSorter

from openai import OpenAI

# LLM API clients
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION", None),
)
fireworks_client = OpenAI(
    api_key=os.environ.get("FIREWORKS_API_KEY"),
    base_url=os.environ.get("FIREWORKS_API_BASE"),
)


# load comm type classes from json
class ConstantsLoader:
    classes = {}  # Dictionary to store dynamically created classes

    @classmethod
    def load_from_json(cls, json_file):
        with open(json_file, "r") as file:
            data = json.load(file)
            for class_name, variables in data.items():
                # Dynamically create a new class
                new_class = type(class_name, (), {})
                # Add static variables to the class
                for key, value in variables.items():
                    setattr(new_class, key, value)
                # Store the newly created class in a dictionary
                cls.classes[class_name] = new_class


ConstantsLoader.load_from_json("frontend/public/constants.json")
globals().update(ConstantsLoader.classes)

# class Status:
#     RECEIVED = "Received"
#     STARTING = "Starting"
#     FINISHED = "Finished"

# class MsgType:
#     STATUS = "status"
#     CONNECTION = "connection"
#     CHAT = "chat"
#     PLAN = "plan"
#     INTERACTION = "interaction"
#     EXECUTE = "execute"
#     RESET = "reset"

# class InteractionType:
#     REPLAN = "replan"


# helper functions
def current_time() -> str:
    return time.strftime("%T")


def create_uuid() -> str:
    return str(uuid.uuid4())[:8]


def topo_sort(graph: dict) -> list:
    sorter = TopologicalSorter(graph)
    return list(sorter.static_order())


if __name__ == "__main__":
    print(Status)
    print(Status.RECEIVED)
    print(MsgType)
    print(MsgType.CHAT)
