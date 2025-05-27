"""Expense analysis using LangChain LLM."""

import json
import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from langchain.schema import HumanMessage, SystemMessage

from app.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class ExpenseAnalyzer:
    """Analyzes messages to extract expense information using LLM."""

    def __init__(self, dev: bool = settings.dev):
        self.dev = dev
        """Initialize the expense analyzer."""
        if self.dev:
            from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

            llm = HuggingFaceEndpoint(
                model=settings.huggingfacehub_model,
                task="text-generation",
                max_new_tokens=512,
                do_sample=False,
                temperature=0.0,
                repetition_penalty=1.03,
                huggingfacehub_api_token=settings.huggingfacehub_api_token,
            )
            self.llm = ChatHuggingFace(llm=llm)
        else:
            from langchain_openai import ChatOpenAI

            self.llm = ChatOpenAI(
                model=settings.llm_model,
                api_key=settings.openai_api_key,
                temperature=0.1,
                max_tokens=500,  # type: ignore
            )

        self.system_prompt = self._create_system_prompt()

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        categories_str = ", ".join(settings.expense_categories)

        return f"""
        You are an intelligent expense parsing assistant.

        Your job is to analyze a user's message and determine if it represents an expense.

        If it **is** an expense, return a **single-line JSON** like this:
        {{
        "is_expense": true,
        "description": "short summary of the expense",
        "amount": number_only,
        "category": one_of({settings.expense_categories})
        }}

        If it is **not** an expense, return:
        {{
        "is_expense": false
        }}

        **IMPORTANT RULES**:
        - Return ONLY the JSON — no extra text, no explanations.
        - Do NOT wrap it in markdown or backticks.
        - Categories must be one of: {categories_str}
        - Amount must be a valid number (no currency symbols, no words like "dollars").

        Examples:

        Input: "Dinner with friends 45"
        Output: {{"is_expense": true, "description": "Dinner with friends", "amount": 45.00, "category": "Food"}}

        Input: "Paid $30 for gas"
        Output: {{"is_expense": true, "description": "Gas", "amount": 30.00, "category": "Transportation"}}

        Input: "hello there!"
        Output: {{"is_expense": false}}

        Now process the next message.
        """

    async def analyze_message(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a message to extract expense information.

        Args:
            message: The user message to analyze

        Returns:
            Dictionary with expense details or None if not an expense
        """
        try:
            # First, do a quick regex check for obvious non-expenses
            if self._is_obviously_not_expense(message):
                logger.debug(f"Message obviously not an expense: {message}")
                return None

            # Use LLM to analyze the message
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=message.strip()),
            ]

            response = await self.llm.ainvoke(messages)
            logger.info(response)
            if self.dev:
                result = self._parse_llm_response(response.content)  # type: ignore
                logger.info(result)
            else:
                result = self._parse_llm_response(response.text())

            if result and result.get("is_expense"):
                # Validate and clean the result
                return self._validate_expense_data(result)

            return None

        except Exception as e:
            logger.error(f"Error analyzing message '{message}': {e}")
            return None

    def _is_obviously_not_expense(self, message: str) -> bool:
        """Quick check for obviously non-expense messages."""
        message_lower = message.lower().strip()

        # Common greetings and non-expense phrases
        non_expense_patterns = [
            r"^(hi|hello|hey|good morning|good afternoon|good evening)",
            r"^(how are you|what\'s up|how\'s it going)",
            r"^(thank you|thanks|thx)",
            r"^(yes|no|ok|okay)",
            r"^\?",  # Questions starting with ?
            r"^(help|start|stop)",
        ]

        for pattern in non_expense_patterns:
            if re.match(pattern, message_lower):
                return True

        # Check if message has any numbers (expenses usually have amounts)
        if not re.search(r"\d", message):
            return True

        return False

    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse the LLM response JSON."""
        try:
            # Clean the response (remove markdown code blocks if present, new lines, etc.)
            response = response.strip()
            response = response.strip("\n")
            response = re.sub(
                r"^(Output:|Result:)", "", response, flags=re.IGNORECASE
            ).strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # Parse JSON
            result = json.loads(response)
            return result

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse LLM response as JSON: {response}. Error: {e}"
            )
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None

    def _validate_expense_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and clean expense data from LLM."""
        try:
            # Check required fields
            if (
                not data.get("description")
                or not data.get("amount")
                or not data.get("category")
            ):
                logger.warning(f"Incomplete expense data: {data}")
                return None

            # Validate category
            category = data["category"].strip()
            if category not in settings.expense_categories:
                logger.warning(f"Invalid category '{category}', using 'Other'")
                category = "Other"

            # Validate and convert amount
            try:
                amount = Decimal(str(data["amount"]))
                if amount <= 0:
                    logger.warning(f"Invalid amount: {amount}")
                    return None
            except (InvalidOperation, ValueError) as e:
                logger.error(f"Failed to convert amount '{data['amount']}': {e}")
                return None

            # Clean description
            description = str(data["description"]).strip()
            if not description:
                logger.warning("Empty description")
                return None

            return {
                "description": description,
                "amount": amount,
                "category": category,
            }

        except Exception as e:
            logger.error(f"Error validating expense data: {e}")
            return None
