import re
from typing import Callable, Self


NON_MARKUP = r"[^_+=!@#$%^[\](){}|<>`~-]"


class Entity:
    start: int
    end: int
    text: str
    is_raw: bool = False

    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

    def to_string(self):
        return self.text[self.start : self.end]

    def __eq__(self, other):
        return (
            other.start == self.start
            and other.end == self.end
            and other.text == self.text
        )

    def __str__(self):
        return f"<{type(self).__name__} {self.start} - {self.end}>"


class Raw(Entity):
    is_raw = True

    def __init__(self, text, start, end):
        super().__init__(text, start, end)

    def get_slice(self, start_offset=0, end_offset=0) -> Self:
        return Raw(self.text, self.start + start_offset, self.end + end_offset)

    @classmethod
    def from_slice(cls, text, start, end):
        if start >= end or text[start:end].isspace():
            return None
        return cls(text, start, end)

    @classmethod
    def from_str(cls, text: str) -> Self:
        return cls(text, 0, len(text))

    def __eq__(self, other):
        return isinstance(other, Raw) and super().__eq__(other)

    def __repr__(self):
        return f'Raw(start={self.start}, end={self.end}, text="{repr(self.text[self.start : self.start + 10])}...")'


class Content:
    content: [Entity]

    def __init__(self, content: [Entity]):
        self.content = content

    @classmethod
    def raw_from_str(cls, text: str) -> Self:
        raw = Raw.from_str(text)
        return cls([raw])

    @classmethod
    def raw_remainder(cls, text: str, start: int, end: int) -> Self:
        return cls([Raw(text, start, end)])

    def to_string(self):
        return "".join(entity.to_string() for entity in self.content)

    def __eq__(self, other):
        if isinstance(other, list):
            for this, that in zip(self.content, other):
                if this != that:
                    return False
            return True
        elif isinstance(other, Content):
            return self == other.content
        return False

    def __repr__(self):
        return f"Content([{',\n'.join(repr(el) for el in self.content)}])"

    @property
    def end(self):
        return self.content[-1].end

    @property
    def start(self):
        return self.content[0].start


class WrappingEntity(Entity):
    tag: str
    content: Content

    def __init__(self, text, start, end, content):
        super().__init__(text, start, end)
        self.content = content

    def to_string(self):
        return f"<{self.tag}>{self.content.to_string()}</{self.tag}>"

    def __eq__(self, other):
        return (
            isinstance(other, WrappingEntity)
            and self.tag == other.tag
            and super().__eq__(other)
            and self.content == other.content
        )

    def __repr__(self):
        return f'''WrappingEntity(
    tag="{self.tag}",
    start={self.start},
    end={self.end},
    text="{repr(self.text[self.start : self.start + 10])}...",
    content={repr(self.content)})'''


class WrappingBlockEntity(WrappingEntity):
    def __init__(self, text, start, end, content):
        super().__init__(text, start, end, content)

    def to_string(self):
        return f"\n<{self.tag}>{self.content.to_string()}</{self.tag}>\n"

    def __repr__(self):
        return f'''WrappingBlockEntity(
    tag="{self.tag}",
    start={self.start},
    end={self.end},
    text="{repr(self.text[self.start : self.start + 10])}...",
    content={repr(self.content)})'''


class Unannotated(Entity):
    def __init__(self, text, start, end):
        super().__init__(start, end)

    def to_string(self):
        return self.text[self.start : self.end]

    def __repr__(self):
        return f'Unannotated(start={self.start}, end={self.end}, text="{repr(self.text[self.start :: self.start + 10])}...")'


class EmEntity(WrappingEntity):
    tag = "em"


class ParagraphEntity(WrappingBlockEntity):
    tag = "p"


class HeaderEntity(WrappingBlockEntity):
    level: int
    is_bof: bool

    def __init__(self, text, start, end, content, *, level, is_bof=False):
        super().__init__(text, start, end, content)
        self.level = level
        self.is_bof = is_bof

    @property
    def tag(self):
        return f"h{self.level}"

    def to_string(self):
        s = super().to_string()
        if self.is_bof:
            return s[1:]
        return s


class Rule:
    pattern: re.Pattern

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        raise NotImplementedError

    @classmethod
    def parse(cls, text: str, start: int, end: int) -> [Entity]:
        content = []
        raw_ix = start
        for match in cls.pattern.finditer(text, start, end):
            if (raw_before := Raw.from_slice(text, raw_ix, match.start())) is not None:
                content.append(raw_before)
            content.append(cls.parse_entity(text, match))
            raw_ix = max(raw_ix, match.end())
        if (raw_after := Raw.from_slice(text, raw_ix, end)) is not None:
            content.append(raw_after)
        return content


class HashHeaderRule(Rule):
    pattern = re.compile(r"(?P<pre>^|\n)(?P<level>#{1,6})\s*(?P<text>.+)")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return HeaderEntity(
            text,
            m.start(),
            m.end(),
            Content.raw_remainder(text, m.start("text"), m.end()),
            level=len(m.group("level")),
            is_bof=(not m.group("pre")),
        )


class EqH1Rule(Rule):
    pattern = re.compile(r"(?P<pre>^|\n)(?P<text>.+)\n={2,}\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return HeaderEntity(
            text,
            m.start(),
            m.end(),
            Content.raw_remainder(text, m.start("text"), m.end("text")),
            level=1,
            is_bof=(not m.group("pre")),
        )


class EqH2Rule(Rule):
    pattern = re.compile(r"(?P<pre>^|\n)(?P<text>.+)\n-{2,}+\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return HeaderEntity(
            text,
            m.start(),
            m.end(),
            Content.raw_remainder(text, m.start("text"), m.end("text")),
            level=2,
            is_bof=(not m.group("pre")),
        )


class Parser:
    blocks: [Rule]
    # finalizer: Callable[[Raw], Content]

    def __init__(self, blocks: [Rule], finalizer=None):
        self.blocks = blocks
        # self.finalizer = finalizer if finalizer is not None else raw_to_unannotated

    def parse(self, text: str) -> Content:
        content = Content.raw_from_str(text)
        for rule in self.blocks:
            content = self.apply_rule(text, rule, content)
        return content

    def apply_rule(self, text: str, rule: Rule, content: Content):
        new_content = []
        for entity in content.content:
            if entity.is_raw:
                new_content.extend(rule.parse(text, entity.start, entity.end))
            else:
                new_content.append(entity)
        return Content(new_content)


def raw_to_unannotated(raw: Raw) -> Content:
    return Unannotated(raw.text, raw.start, raw.end)


# class ParagraphRule(Rule):
#     pattern = re.compile(
#         r"(?P<lead>\n{2})(?P<content>((.|\n)+(?!\n{2})))(?P<trail>\n{2}|$)"
#     )
