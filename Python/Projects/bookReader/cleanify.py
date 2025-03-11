"""This file is part of the bookReader project. it is a complex program that makes any ebook "clean", removing swear words and phrases.
It can also use AI to rewrite the text, removing any NSFW content and making it more appropriate.
"""

import encoder
import re


class EbookContext:
    def __init__(
        self,
        rating: str = ("G", "PG", "PG-13"),
        AiRevision: bool = False,
        AiRecursiveRevisionLevel: int = 1,
        AiRevisionModel: str = ("GPT-3.5", "GPT-4"),
    ):
        """
        Args:
            rating (str): The rating of the ebook. Can be "G", "PG", or "PG-13".
            AiRevision (bool): Whether to use AI for revision.
            AiRecursiveRevisionLevel (int): The level of recursive revision.
            AiRevisionModel (str): The model to use for AI revision.
        """
        self.rating = rating
        self.AiRevision = AiRevision
        self.AiRecursiveRevisionLevel = AiRecursiveRevisionLevel
        self.AiRevisionModel = AiRevisionModel


class Purger:
    def __init__(self, EbookContext: EbookContext):
        self.EbookContext = EbookContext
        self.badwords = "1&NmM2NDc2Njc=\n1&NzU2YTY5NzQ=\n1&NzQ3NDYy\n1&Njg2ZjZhNmM2NDc2Njc=\n1&NjY2ZDcwNjk3NDc0NjI=\n1&N2E3NTc1NmE2OTc0"
        self.badwords = self.badwords.splitlines()
        for i in range(len(self.badwords)):
            self.badwords[i] = encoder.Ciphers.Decoders.level_4(
                self.badwords[i].strip()
            )
            self.badwords[i] = f" {self.badwords[i]} "

    def cleanify(self, text: str) -> str:
        """
        Cleans the text by removing bad words and phrases based on the rating.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        removed_words_count = {}
        for word in self.badwords:
            if self.EbookContext.rating == "G":
                occurrences = len(re.findall(word, text, flags=re.IGNORECASE))
                text = re.sub(word, "*" * len(word), text, flags=re.IGNORECASE)
            elif self.EbookContext.rating == "PG":
                occurrences = len(re.findall(word, text, flags=re.IGNORECASE))
                text = re.sub(
                    word, word[1] + "*" * (len(word) - 3), text, flags=re.IGNORECASE
                )
            elif self.EbookContext.rating == "PG-13":
                occurrences = len(re.findall(word, text, flags=re.IGNORECASE))
                text = re.sub(
                    word,
                    word[1] + "*" * (len(word) - 4) + word[-2],
                    text,
                    flags=re.IGNORECASE,
                )
            if occurrences > 0:
                removed_words_count[word[1] + "*" * (len(word) - 4) + word[-2]] = (
                    occurrences
                )
        for word, count in removed_words_count.items():
            print(f"Removed {count} occurrences of {word}.")
        return text

    def cleanify_with_ai(self, text: str) -> str:
        """
        Cleans the text using AI revision.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        if self.EbookContext.AiRevision:
            return self.cleanify(text)  # Placeholder for AI revision logic
        else:
            # Use the default cleanify method
            return self.cleanify(text)
