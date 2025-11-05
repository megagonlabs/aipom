import json
import os
import time
import uuid

from openai import OpenAI

# LLM API clients
openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
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


# helper functions
def current_time() -> str:
    return time.strftime("%T")


def create_uuid() -> str:
    return str(uuid.uuid4())[:8]
