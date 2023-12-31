import unittest
from unittest.mock import patch, MagicMock
from hestia.llm.llama_chat_completion import chat_completion

class TestChatCompletion(unittest.TestCase):
    @patch('hestia.llm.llama_chat_completion.load_llama_model')
    def test_chat_completion(self, mock_load_llama_model):
        # Arrange
        mock_llm = MagicMock()
        mock_load_llama_model.return_value.__enter__.return_value = mock_llm
        mock_llm.create_chat_completion.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test content"
                    }
                }
            ]
        }
        system_prompt = "System prompt"
        user_prompt = "User prompt"

        # Act
        result = chat_completion(system_prompt, user_prompt)

        # Assert
        mock_load_llama_model.assert_called_once()
        mock_llm.create_chat_completion.assert_called_once_with(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ], 
            max_tokens=1024
        )
        self.assertEqual(result, "Test content")

if __name__ == '__main__':
    unittest.main()