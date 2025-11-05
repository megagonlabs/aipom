from abc import ABC, abstractmethod

from custom_types import NodeInputVars


class BaseAgent(ABC):
    """
    Abstract base class for agents.
    All agents must implement the execute() method.
    """
    @abstractmethod
    def execute(self, task: str, input_vars: NodeInputVars, output_vars: list[str], *args, **kwargs) -> dict:
        """
        Execute the agent's task.
        """
        pass
