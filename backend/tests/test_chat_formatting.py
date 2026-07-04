import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import format_chat_reply


class ChatFormattingTests(unittest.TestCase):
    def test_format_chat_reply_returns_bullets_and_stays_short(self):
        long_reply = (
            "Here is a very detailed explanation of your current situation. "
            "You should review spending and protect your runway this week. "
            "A small marketing push could help sales recover."
        )

        result = format_chat_reply(long_reply)

        self.assertIn("•", result)
        self.assertLessEqual(result.count("•"), 3)
        self.assertLess(len(result), 250)


if __name__ == "__main__":
    unittest.main()
