import re
from .entity import (
    Content,
    Entity,
    HeaderEntity,
    ListItemEntity,
    OrderedListEntity,
    PreEntity,
    Raw,
    UnorderedListEntity,
)


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


class ListLikeRule(Rule):
    list_entity: Entity
    item_pattern: re.Pattern
    pattern: re.Pattern

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        list_el = cls.list_entity(text, m.start(), m.end(), [])
        matches = cls.item_pattern.finditer(text, m.start(), m.end())
        curr_indent = 0
        lists = [list_el]
        for match in matches:
            ind = parse_indent(match.group("indent"))
            li = ListItemEntity(
                text,
                match.start(),
                match.end(),
                Content.raw_remainder(text, match.start("text"), match.end("text")),
            )
            if ind > curr_indent:
                inner = cls.list_entity(text, match.start(), m.end(), [li])
                lists[curr_indent].push_item(inner)
                lists.append(inner)
                curr_indent += 1
            elif ind < curr_indent:
                lists[ind].push_item(li)
                curr_indent = ind
            else:
                lists[curr_indent].push_item(li)
        for lst in lists:
            lst.trim_to_content()
        return list_el


class OlRule(ListLikeRule):
    list_entity = OrderedListEntity
    ITEM_PAT = r"(\n(?P<indent>(\t| {2,}))?\d+\.[\t ]+(?P<text>.+))"
    item_pattern = re.compile(ITEM_PAT)
    pattern = re.compile("\n" + ITEM_PAT + "+\n")


class UlRule(ListLikeRule):
    list_entity = UnorderedListEntity
    ITEM_PAT = r"(\n(?P<indent>(\t| {2,}))?[-*+][\t ]+(?P<text>.+))"
    item_pattern = re.compile(ITEM_PAT)
    pattern = re.compile("\n" + ITEM_PAT + "+\n")


class FencedPreRule(Rule):
    pattern = re.compile(r"\n(```|~~~)(?P<lang>\w+)?\n(?P<text>(.|\n)+)\1\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return PreEntity(text, m.start(), m.end(), m.group("lang"), m.group("text"))


def parse_indent(indent: str | None) -> int:
    if indent is None:
        return 0
    return len(indent.replace("\t", "  ")) // 2
