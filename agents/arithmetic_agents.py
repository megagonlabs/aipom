from custom_types import NodeInputVars

from .base_agent import BaseAgent


class AddAgent(BaseAgent):
    def __init__(self):
        self.config = {}
    def execute(self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict) -> dict:
        operands = [float(val) for _, val in input_vars]
        return {
            output_vars[0]: sum(operands)
        }


class MultiplyAgent(BaseAgent):
    def __init__(self):
        self.config = {}
    def execute(self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict) -> dict:
        result = 1
        operands = [float(val) for _, val in input_vars]
        for operand in operands:
            result *= operand
        return {
            output_vars[0]: result
        }


class SubtractAgent(BaseAgent):
    def __init__(self):
        self.config = {}
    def execute(self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict) -> dict:
        operands = [float(val) for _, val in input_vars]
        result = operands[0]
        for operand in operands[1:]:
            result -= operand
        return {
            output_vars[0]: result
        }


class DivideAgent(BaseAgent):
    def __init__(self):
        self.config = {}
    def execute(self, task: str, input_vars: NodeInputVars, output_vars: list[str], params: dict) -> dict:
        operands = [float(val) for _, val in input_vars]
        if 0 in operands[1:]:
            return "Error: Division by zero"
        result = operands[0]
        for operand in operands[1:]:
            result /= operand
        return {
            output_vars[0]: result
        }