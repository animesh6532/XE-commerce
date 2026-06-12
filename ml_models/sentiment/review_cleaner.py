import re
import string


class ReviewCleaner:

    @staticmethod
    def clean(text):

        if not isinstance(text, str):
            return ""

        text = text.lower()

        text = re.sub(
            r"http\S+",
            "",
            text
        )

        text = re.sub(
            r"<.*?>",
            "",
            text
        )

        text = re.sub(
            r"\d+",
            "",
            text
        )

        text = text.translate(
            str.maketrans(
                "",
                "",
                string.punctuation
            )
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()