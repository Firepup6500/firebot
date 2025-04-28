# pylint: skip-file
import random
from typing import Union


class MarkovBot:
    def __init__(self, text: list[list[str]]) -> None:
        self.text = text
        self.chains = {}
        self.__build_chains()

    def __build_chains(self) -> None:
        for i in range(len(self.text)):
            text = self.text[i]
            for j in range(len(text) - 1):
                current_word = text[j]
                next_word = text[j + 1]

                if current_word not in self.chains:
                    self.chains[current_word] = {}

                if next_word not in self.chains[current_word]:
                    self.chains[current_word][next_word] = 0

                self.chains[current_word][next_word] += 1

    def generate_text(self, word: Union[str, None] = None) -> str:
        if not word:
            current_word = random.choice(list(self.chains.keys()))
        else:
            current_word = word
        generated_text = current_word

        while current_word in self.chains:
            next_word = random.choices(
                list(self.chains[current_word].keys()),
                weights=list(self.chains[current_word].values()),
            )[0]
            generated_text += " " + next_word
            current_word = next_word

        return generated_text

    def generate_from_sentence(self, msg: Union[str, None] = None) -> str:
        if not msg:
            word = random.choice(list(self.chains.keys()))
        else:
            word = random.choice(msg.split())
        if (for_word := self.generate_text(word)) != word:
            return for_word
        else:
            return self.generate_text()
