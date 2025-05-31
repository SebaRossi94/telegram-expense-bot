"""Tests for the ExpenseAnalyzer class."""

import json
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.expense_analyzer import ExpenseAnalyzer


class TestExpenseAnalyzer:
    """Test cases for ExpenseAnalyzer class."""

    def test_init_dev_mode(self, expense_analyzer_dev):
        """Test ExpenseAnalyzer initialization in dev mode."""
        assert expense_analyzer_dev.dev is True
        assert expense_analyzer_dev.llm is not None
        assert expense_analyzer_dev.system_prompt is not None

    def test_init_prod_mode(self, expense_analyzer_prod):
        """Test ExpenseAnalyzer initialization in production mode."""
        assert expense_analyzer_prod.dev is False
        assert expense_analyzer_prod.llm is not None
        assert expense_analyzer_prod.system_prompt is not None

    def test_system_prompt_contains_categories(
        self, expense_analyzer_dev, expense_categories
    ):
        """Test that system prompt contains all expense categories."""
        system_prompt = expense_analyzer_dev.system_prompt
        for category in expense_categories:
            assert category in system_prompt

    def test_system_prompt_format(self, expense_analyzer_dev):
        """Test that system prompt has expected format and instructions."""
        prompt = expense_analyzer_dev.system_prompt
        assert "expense parsing assistant" in prompt
        assert "single-line JSON" in prompt
        assert '"is_expense": true' in prompt
        assert '"is_expense": false' in prompt
        assert "IMPORTANT RULES" in prompt

    @pytest.mark.parametrize(
        "message",
        [
            "hi there",
            "hello",
            "good morning",
            "how are you",
            "thank you",
            "yes",
            "help",
            "random text without numbers",
        ],
    )
    def test_is_obviously_not_expense(self, expense_analyzer_dev, message):
        """Test detection of obviously non-expense messages."""
        result = expense_analyzer_dev._is_obviously_not_expense(message)
        assert result is True

    @pytest.mark.parametrize(
        "message",
        [
            "spent 25 on lunch",
            "dinner cost $30",
            "paid 15 for coffee",
            "grocery shopping 85.50",
        ],
    )
    def test_is_not_obviously_not_expense(self, expense_analyzer_dev, message):
        """Test that potential expense messages are not filtered out."""
        result = expense_analyzer_dev._is_obviously_not_expense(message)
        assert result is False

    def test_parse_llm_response_valid_json(
        self, expense_analyzer_dev, valid_expense_response
    ):
        """Test parsing valid JSON response from LLM."""
        result = expense_analyzer_dev._parse_llm_response(valid_expense_response)

        assert result is not None
        assert result["is_expense"] is True
        assert result["description"] == "Lunch at restaurant"
        assert result["amount"] == 25.50
        assert result["category"] == "Food"

    def test_parse_llm_response_invalid_json(
        self, expense_analyzer_dev, malformed_json_response
    ):
        """Test parsing malformed JSON response from LLM."""
        result = expense_analyzer_dev._parse_llm_response(malformed_json_response)
        assert result is None

    def test_parse_llm_response_with_markdown(
        self, expense_analyzer_dev, expense_with_markdown_response
    ):
        """Test parsing JSON response wrapped in markdown code blocks."""
        result = expense_analyzer_dev._parse_llm_response(
            expense_with_markdown_response
        )

        assert result is not None
        assert result["is_expense"] is True
        assert result["description"] == "Coffee"
        assert result["amount"] == 4.50
        assert result["category"] == "Food"

    def test_parse_llm_response_with_output_prefix(self, expense_analyzer_dev):
        """Test parsing response with 'Output:' prefix."""
        response = 'Output: {"is_expense": true, "description": "Test", "amount": 10, "category": "Food"}'
        result = expense_analyzer_dev._parse_llm_response(response)

        assert result is not None
        assert result["is_expense"] is True
        assert result["description"] == "Test"

    def test_validate_expense_data_valid(
        self, expense_analyzer_dev, sample_expense_data
    ):
        """Test validation of valid expense data."""
        input_data = {
            "description": "Lunch at restaurant",
            "amount": 25.50,
            "category": "Food",
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)

        assert result is not None
        assert result["description"] == "Lunch at restaurant"
        assert result["amount"] == Decimal("25.50")
        assert result["category"] == "Food"

    def test_validate_expense_data_invalid_category(self, expense_analyzer_dev):
        """Test validation with invalid category defaults to 'Other'."""
        input_data = {
            "description": "Test expense",
            "amount": 25.50,
            "category": "InvalidCategory",
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)

        assert result is not None
        assert result["category"] == "Other"

    @pytest.mark.parametrize(
        "invalid_data",
        [
            # Missing description
            {"amount": 25.50, "category": "Food"},
            # Missing amount
            {"description": "Lunch", "category": "Food"},
            # Missing category
            {"description": "Lunch", "amount": 25.50},
            # Negative amount
            {"description": "Lunch", "amount": -25.50, "category": "Food"},
            # Zero amount
            {"description": "Lunch", "amount": 0, "category": "Food"},
            # Empty description
            {"description": "", "amount": 25.50, "category": "Food"},
        ],
    )
    def test_validate_expense_data_invalid_cases(
        self, expense_analyzer_dev, invalid_data
    ):
        """Test validation of various invalid expense data cases."""
        result = expense_analyzer_dev._validate_expense_data(invalid_data)
        assert result is None

    def test_validate_expense_data_string_amount(self, expense_analyzer_dev):
        """Test validation converts string amounts to Decimal."""
        input_data = {
            "description": "Test expense",
            "amount": "25.50",
            "category": "Food",
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)

        assert result is not None
        assert result["amount"] == Decimal("25.50")
        assert isinstance(result["amount"], Decimal)

    def test_validate_expense_data_invalid_amount_string(self, expense_analyzer_dev):
        """Test validation fails with non-numeric amount string."""
        input_data = {
            "description": "Test expense",
            "amount": "twenty-five",
            "category": "Food",
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_message_valid_expense(
        self, expense_analyzer_dev, mock_llm_response, valid_expense_response
    ):
        """Test analyzing a valid expense message."""
        # Setup mock LLM response
        mock_response = mock_llm_response(valid_expense_response)
        expense_analyzer_dev.llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await expense_analyzer_dev.analyze_message("Spent $25.50 on lunch")

        assert result is not None
        assert result["description"] == "Lunch at restaurant"
        assert result["amount"] == Decimal("25.50")
        assert result["category"] == "Food"

    @pytest.mark.asyncio
    async def test_analyze_message_not_expense(
        self, expense_analyzer_dev, mock_llm_response, invalid_expense_response
    ):
        """Test analyzing a non-expense message."""
        # Setup mock LLM response
        mock_response = mock_llm_response(invalid_expense_response)
        expense_analyzer_dev.llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await expense_analyzer_dev.analyze_message("Hello there!")

        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_message_obviously_not_expense(self, expense_analyzer_dev):
        """Test that obviously non-expense messages are filtered out early."""
        result = await expense_analyzer_dev.analyze_message("hello")
        assert result is None

        # Ensure LLM was not called for obviously non-expense messages
        expense_analyzer_dev.llm.ainvoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_analyze_message_llm_exception(self, expense_analyzer_dev):
        """Test handling of LLM exceptions."""
        # Setup mock to raise exception
        expense_analyzer_dev.llm.ainvoke = AsyncMock(side_effect=Exception("LLM Error"))

        result = await expense_analyzer_dev.analyze_message("Spent $25 on lunch")

        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_message_malformed_llm_response(
        self, expense_analyzer_dev, mock_llm_response, malformed_json_response
    ):
        """Test handling of malformed LLM response."""
        # Setup mock LLM response with malformed JSON
        mock_response = mock_llm_response(malformed_json_response)
        expense_analyzer_dev.llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await expense_analyzer_dev.analyze_message("Spent $25 on lunch")

        assert result is None

    @pytest.mark.asyncio
    async def test_analyze_message_dev_vs_prod_response_handling(
        self, expense_analyzer_prod, mock_llm_response, valid_expense_response
    ):
        """Test that dev and prod modes handle LLM responses differently."""
        # Setup mock LLM response for production mode
        mock_response = mock_llm_response(valid_expense_response)
        expense_analyzer_prod.llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await expense_analyzer_prod.analyze_message("Spent $25.50 on lunch")

        assert result is not None
        assert result["description"] == "Lunch at restaurant"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "message,expected_not_none",
        [
            ("Spent $25 on lunch", True),
            ("Coffee $4.50", True),
            ("Paid 30 for gas", True),
            ("hello there", False),
            ("how are you", False),
            ("thanks", False),
        ],
    )
    async def test_analyze_message_various_inputs(
        self, expense_analyzer_dev, mock_llm_response, message, expected_not_none
    ):
        """Test analyze_message with various input types."""
        if expected_not_none:
            # Mock valid expense response
            response_content = '{"is_expense": true, "description": "Test expense", "amount": 25.00, "category": "Food"}'
        else:
            # Mock non-expense response
            response_content = '{"is_expense": false}'

        mock_response = mock_llm_response(response_content)
        expense_analyzer_dev.llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await expense_analyzer_dev.analyze_message(message)

        if expected_not_none:
            assert result is not None
        else:
            assert result is None

    def test_decimal_precision_handling(self, expense_analyzer_dev):
        """Test that Decimal amounts maintain precision."""
        input_data = {
            "description": "Test expense",
            "amount": "25.999",  # More than 2 decimal places
            "category": "Food",
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)

        assert result is not None
        assert result["amount"] == Decimal("25.999")
        assert str(result["amount"]) == "25.999"

    def test_whitespace_handling_in_validation(self, expense_analyzer_dev):
        """Test that whitespace is properly handled in validation."""
        input_data = {
            "description": "  Test expense  ",
            "amount": 25.50,
            "category": "  Food  ",
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)

        assert result is not None
        assert result["description"] == "Test expense"
        assert result["category"] == "Food"

    @pytest.mark.asyncio
    async def test_empty_message_handling(self, expense_analyzer_dev):
        """Test handling of empty or whitespace-only messages."""
        result = await expense_analyzer_dev.analyze_message("")
        assert result is None

        result = await expense_analyzer_dev.analyze_message("   ")
        assert result is None

    def test_category_case_sensitivity(self, expense_analyzer_dev):
        """Test that category validation is case-sensitive."""
        input_data = {
            "description": "Test expense",
            "amount": 25.50,
            "category": "food",  # lowercase, should be "Food"
        }

        result = expense_analyzer_dev._validate_expense_data(input_data)

        assert result is not None
        assert result["category"] == "Other"  # Should default to Other

    def test_parse_llm_response_general_exception(self, expense_analyzer_dev):
        """Test handling of general exceptions in _parse_llm_response."""
        with patch("json.loads") as mock_loads:
            mock_loads.side_effect = Exception("Unexpected error")
            result = expense_analyzer_dev._parse_llm_response('{"not": "valid"}')
            assert result is None

    def test_validate_expense_data_general_exception(self, expense_analyzer_dev):
        """Test handling of general exceptions in _validate_expense_data."""
        # Create a real data dictionary that will cause an exception
        input_data = {
            "description": "Test",
            "amount": complex(
                1, 2
            ),  # Using complex number will cause an exception in Decimal conversion
            "category": "Food",
        }
        result = expense_analyzer_dev._validate_expense_data(input_data)
        assert result is None

    def test_validate_expense_data_type_error(self, expense_analyzer_dev):
        """Test handling of TypeError in _validate_expense_data."""
        input_data = {
            "description": None,  # This will cause a TypeError when calling strip()
            "amount": 25.50,
            "category": "Food",
        }
        result = expense_analyzer_dev._validate_expense_data(input_data)
        assert result is None

    def test_validate_expense_data_invalid_decimal_conversion(
        self, expense_analyzer_dev
    ):
        """Test handling of invalid decimal conversion."""
        input_data = {
            "description": "Test expense",
            "amount": "not.a.number",
            "category": "Food",
        }
        result = expense_analyzer_dev._validate_expense_data(input_data)
        assert result is None
