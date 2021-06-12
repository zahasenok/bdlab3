from random import randint, choice
from enum import Enum


class Tags(Enum):
    work = 1
    advertisement = 2
    notification = 3

    @classmethod
    def has_member(cls, value):
        return value in Tags._member_names_

    @classmethod
    def get_random(cls):
        tags = []
        num = randint(0, len(Tags))
        for i in range(num):
            tag = choice(list(Tags)).name
            if tag not in tags:
                tags.append(tag)
        return tags
