"""Pytest configuration and fixtures."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain.schema import AIMessage

from app.expense_analyzer import ExpenseAnalyzer


@pytest.fixture
def expense_categories():
    """Fixture providing the list of expense categories."""
    return [
        "Food",
        "Transportation",
        "Entertainment",
        "Shopping",
        "Bills",
        "Healthcare",
        "Other",
    ]


@pytest.fixture
def mock_llm_response():
    """Factory fixture for creating mock LLM responses."""

    def _create_response(content: str) -> AIMessage:
        mock_response = MagicMock()
        mock_response.content = content
        mock_response.text.return_value = content
        return mock_response

    return _create_response


@pytest.fixture
def expense_analyzer_dev():
    """Fixture for ExpenseAnalyzer in dev mode."""
    with pytest.MonkeyPatch().context():
        # Mock the HuggingFace imports and classes
        mock_chat_hf = AsyncMock()

        analyzer = ExpenseAnalyzer(dev=True)
        analyzer.llm = mock_chat_hf
        yield analyzer


@pytest.fixture
def expense_analyzer_prod():
    """Fixture for ExpenseAnalyzer in production mode."""
    with pytest.MonkeyPatch().context():
        # Mock the OpenAI imports and classes
        mock_chat_openai = AsyncMock()

        analyzer = ExpenseAnalyzer(dev=False)
        analyzer.llm = mock_chat_openai
        yield analyzer


@pytest.fixture
def valid_expense_response():
    """Fixture providing a valid expense JSON response."""
    return '{"is_expense": true, "description": "Lunch at restaurant", "amount": 25.50, "category": "Food"}'


@pytest.fixture
def invalid_expense_response():
    """Fixture providing an invalid expense JSON response."""
    return '{"is_expense": false}'


@pytest.fixture
def malformed_json_response():
    """Fixture providing a malformed JSON response."""
    return '{"is_expense": true, "description": "Lunch", "amount": 25.50, "category": "Food"'  # Missing closing brace


@pytest.fixture
def expense_with_markdown_response():
    """Fixture providing an expense response wrapped in markdown."""
    return '```json\n{"is_expense": true, "description": "Coffee", "amount": 4.50, "category": "Food"}\n```'


@pytest.fixture
def sample_expense_messages():
    """Fixture providing sample expense messages for testing."""
    return [
        "Spent $25 on lunch",
        "Dinner with friends 45",
        "Paid 30 for gas",
        "Coffee 4.50",
        "Movie tickets $15 each, bought 2",
        "Grocery shopping 85.50",
        "Uber ride home 12",
        "Doctor visit 150",
        "Phone bill 60",
    ]


@pytest.fixture
def sample_non_expense_messages():
    """Fixture providing sample non-expense messages for testing."""
    return [
        "Hello there!",
        "How are you?",
        "Thanks for your help",
        "Good morning",
        "Yes",
        "No",
        "Help me with something",
        "What's the weather like?",
        "Can you help me?",
        "Random text without numbers",
    ]


@pytest.fixture
def sample_expense_data():
    """Fixture providing sample validated expense data."""
    return {
        "description": "Lunch at restaurant",
        "amount": Decimal("25.50"),
        "category": "Food",
    }


@pytest.fixture
def invalid_expense_data_samples():
    """Fixture providing various invalid expense data samples."""
    return [
        # Missing description
        {"amount": 25.50, "category": "Food"},
        # Missing amount
        {"description": "Lunch", "category": "Food"},
        # Missing category
        {"description": "Lunch", "amount": 25.50},
        # Invalid amount (negative)
        {"description": "Lunch", "amount": -25.50, "category": "Food"},
        # Invalid amount (zero)
        {"description": "Lunch", "amount": 0, "category": "Food"},
        # Invalid amount (non-numeric string)
        {"description": "Lunch", "amount": "twenty-five", "category": "Food"},
        # Invalid category
        {"description": "Lunch", "amount": 25.50, "category": "InvalidCategory"},
        # Empty description
        {"description": "", "amount": 25.50, "category": "Food"},
        # None values
        {"description": None, "amount": 25.50, "category": "Food"},
    ]
