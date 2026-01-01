import re
from .entity import Content, Entity, HeaderEntity, Raw


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


# def raw_to_unannotated(raw: Raw) -> Content:
#     return Unannotated(raw.text, raw.start, raw.end)
