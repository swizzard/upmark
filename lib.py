import re
from typing import Protocol


class Annotated(Protocol):
    def start_pos(self) -> int: ...
    def end_pos(self) -> int: ...
    def as_str(self) -> str: ...


class Bare:
    content: str
    start: int
    end: int

    def as_str(self) -> str:
        return self.content

    def start_pos(self) -> int:
        return self.start

    def end_pos(self) -> int:
        return self.end

    def __str__(self):
        return self.as_str()


class Tag:
    start: int
    end: int

    def start_pos(self) -> int:
        return self.start

    def end_pos(self) -> int:
        return self.end

    def as_str(self) -> str:
        raise NotImplementedError


# class InlineTag(Tag):
#     """
#     _content_ -> <i>content</i>
#     """
#     tag: str
#     content: str

#     def __init__(self, content, tag):
#         self.content = content
#         self.tag = tag

#     def as_str(self) -> str:
#         return f'<{self.tag}>{self.content}</{self.tag}>'


# class LinkLikeTag(Tag):
#     """
#     [name](url "title") -> <a href="url" title="title">name</a>
#     """
#     tag: str
#     segments: [str]


# class


class Annotation:
    pat: re.Pattern
    priority: int

    def matches(self, inp: str) -> [Tag]:
        raise NotImplementedError


class Inline(Annotation):
    priority = 0
    pass


class LinkLike(Annotation):
    priority = 1
    pass


class Block(Annotation):
    priority = 2
    pass


class HeaderLike(Annotation):
    priority = 4
    pass


class ListLike(Annotation):
    priority = 3
    pass


class Parser:
    annotations: dict[int, [Annotation]]
    results: [Annotated]

    def __init__(self, annotations: [Annotation]):
        self.annotations = {0: [], 1: [], 2: [], 3: [], 4: []}
        for annotation in annotations:
            self.annotations[annotation.priority].append(annotation)
        self.results = []

    def parse(self, inp: str):
        for priority in (4, 3, 2):
            for annotation in self.annotations[priority]:
                self.results.append(annotation.matches(inp))
        self.order_results()

    def order_results(self):
        # TODO: sort results by start/end
        pass
