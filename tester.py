import unittest
from unittest.mock import patch, MagicMock
from file_for_test import CatFactProcessor, APIError
import requests


class TestCatFactProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CatFactProcessor()

    @patch("requests.get")
    def test_get_fact_successful_response(self, mock_get):


        sample_fact = "Cats have five toes on their front paws."

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"fact": sample_fact}
        mock_get.return_value = mock_response

        result = self.processor.get_fact()

        self.assertEqual(result, sample_fact)
        self.assertEqual(self.processor.last_fact, sample_fact)
        mock_get.assert_called_once_with(
            "https://catfact.ninja/fact", timeout=5
        )

    @patch("requests.get")
    def test_get_fact_raises_api_error_on_request_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        with self.assertRaises(APIError) as context:
            self.processor.get_fact()

        self.assertIn("Ошибка при запросе к API", str(context.exception))

    def test_get_fact_analysis_returns_zero_when_no_fact(self):

        result = self.processor.get_fact_analysis()
        self.assertEqual(result, {"length": 0, "letter_frequencies": {}})

    def test_get_fact_analysis_returns_correct_analysis(self):

        self.processor.last_fact = "Cats are cute!"

        result = self.processor.get_fact_analysis()

        self.assertEqual(result["length"], 14)

        expected_freq = {
            "c": 2,
            "a": 2,
            "t": 2,
            "s": 1,
            "r": 1,
            "e": 2,
            "u": 1,
        }
        self.assertEqual(result["letter_frequencies"], expected_freq)


def test_get_fact_analysis_is_case_insensitive_and_ignores_non_alpha(self):

    self.processor.last_fact = "AaA! 123 bBb??"

    result = self.processor.get_fact_analysis()

    self.assertEqual(result["length"], len("AaA! 123 bBb??"))
    self.assertEqual(result["letter_frequencies"], {"a": 3, "b": 3})


def test_get_fact_does_not_mutate_on_exception(self):
    self.processor.last_fact = "Existing fact"
    with patch(
        "requests.get", side_effect=requests.exceptions.RequestException
    ):
        with self.assertRaises(APIError):
            self.processor.get_fact()

    self.assertEqual(self.processor.last_fact, "Existing fact")


if __name__ == "__main__":
    unittest.main()
