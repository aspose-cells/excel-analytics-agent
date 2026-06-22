from openai import OpenAI
from config import OPENAI_API_KEY, MODEL, OPENAI_BASE_URL
from app.llm.prompts.tool_selection_prompt import TOOL_SELECTION_PROMPT
from app.logger import logger
from app.exceptions import PlannerError
import json
from typing import Any, Dict

client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )


class Planner:
    """LLM-based planner that creates analysis plans from user requests."""

    def create_plan(self, request: str) -> Dict[str, Any]:
        """Create an analysis plan from a user request using the LLM.

        Args:
            request: User's natural language request.

        Returns:
            Dict containing the analysis plan with a 'tools' key.

        Raises:
            PlannerError: If the LLM output is invalid or the plan is malformed.
        """
        logger.info(f"Creating plan for request: {request[:50]}...")
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": TOOL_SELECTION_PROMPT
                    },
                    {
                        "role": "user",
                        "content": request
                    }
                ]
            )

            content = response.choices[0].message.content
            try:
                plan = json.loads(content)
            except Exception as e:
                logger.error(f"LLM output is not valid JSON: {content}")
                raise PlannerError(f"LLM output is not valid JSON: {content}") from e

            if isinstance(plan, list):
                plan = {"tools": plan}

            if "tools" not in plan:
                logger.error(f"Invalid plan format: {plan}")
                raise PlannerError(f"Invalid plan format: {plan}")

            logger.info(f"Plan created with tools: {plan.get('tools', [])}")
            return plan

        except PlannerError:
            raise
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            raise PlannerError(f"Planner failed: {e}") from e


"""       
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": TOOL_SELECTION_PROMPT},
                {"role": "user", "content": request}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "select_tools",
                        "description": "Select best analysis tools for Excel data analysis",  #  must be string
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "tools": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "reason": {
                                    "type": "string"
                                },
                                "confidence": {
                                    "type": "number"
                                }
                            },
                            "required": ["tools"]
                        }
                    }
                }
            ],
            tool_choice="auto",
            temperature=0.2
        )

        msg = response.choices[0].message

        # tool calling
        if msg.tool_calls:
            args = msg.tool_calls[0].function.arguments
            return json.loads(args)

        # fallback
        return json.loads(msg.content)
"""