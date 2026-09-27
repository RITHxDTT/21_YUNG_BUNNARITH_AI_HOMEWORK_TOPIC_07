from enum import Enum
from pydantic import ValidationError

from database.schemas import (
    UserRole,
    SearchProductsInput,
    CheckStockInput,
    DeleteProductInput,
)

from tools import (
    search_products,
    check_stock,
    delete_product,
)



# Tool Risk

class ToolRisk(str, Enum):
    READ_ONLY = "READ_ONLY"
    WRITE = "WRITE"
    DESTRUCTIVE = "DESTRUCTIVE"



# Tool Registry


TOOL_REGISTRY = {

    "search_products": {
        "function": search_products,
        "schema": SearchProductsInput,
        "allowed_roles": [
            UserRole.CUSTOMER,
            UserRole.ADMIN,
        ],
        "risk": ToolRisk.READ_ONLY,
    },

    "check_stock": {
        "function": check_stock,
        "schema": CheckStockInput,
        "allowed_roles": [
            UserRole.CUSTOMER,
            UserRole.ADMIN,
        ],
        "risk": ToolRisk.READ_ONLY,
    },

    "delete_product": {
        "function": delete_product,
        "schema": DeleteProductInput,
        "allowed_roles": [
            UserRole.ADMIN,
        ],
        "risk": ToolRisk.DESTRUCTIVE,
    },
}



# Harness


class AgentHarness:

    def __init__(
        self,
        user_role: UserRole,
        max_tool_calls: int = 5,
    ):
        self.user_role = user_role
        self.max_tool_calls = max_tool_calls
        self.tool_call_count = 0



    # Get Tool Risk

    def get_risk(self, tool_name: str):

        tool_config = TOOL_REGISTRY.get(tool_name)

        if tool_config is None:
            return None

        return tool_config["risk"]


    # human tool need Approval?


    def needs_approval(self, tool_name: str):

        risk = self.get_risk(tool_name)

        return risk in [
            ToolRisk.WRITE,
            ToolRisk.DESTRUCTIVE,
        ]



    # Validate Tool


    def validate(self, tool_name: str, arguments: dict):

        # Tool-call limit
        if self.tool_call_count >= self.max_tool_calls:
            return {
                "success": False,
                "error": "Maximum tool-call limit reached.",
            }

        # Tool allowlist
        tool_config = TOOL_REGISTRY.get(tool_name)

        if tool_config is None:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
            }

        # Permission
        if self.user_role not in tool_config["allowed_roles"]:
            return {
                "success": False,
                "error": (
                    f"Permission denied. "
                    f"Role '{self.user_role.value}' "
                    f"cannot use '{tool_name}'."
                ),
            }

        # Input validation
        try:

            validated_input = tool_config["schema"](
                **arguments
            )

        except ValidationError as error:

            return {
                "success": False,
                "error": "Invalid tool arguments.",
                "details": error.errors(),
            }

        return {
            "success": True,
            "validated_input": validated_input,
        }



    # Execute Tool


    def execute(self, tool_name: str, arguments: dict):

        validation = self.validate(
            tool_name,
            arguments,
        )

        if not validation["success"]:
            return validation

        tool_config = TOOL_REGISTRY[tool_name]

        validated_input = validation["validated_input"]

        try:

            self.tool_call_count += 1

            result = tool_config["function"](
                **validated_input.model_dump()
            )

            return {
                "success": True,
                "tool": tool_name,
                "risk": tool_config["risk"].value,
                "result": result,
            }

        except Exception as error:

            return {
                "success": False,
                "error": (
                    f"Tool execution failed: {str(error)}"
                ),
            }