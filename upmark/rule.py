import re
from . import entity
from .entity import Content, Entity


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
            if (
                raw_before := entity.Raw.from_slice(text, raw_ix, match.start())
            ) is not None:
                content.append(raw_before)
            content.append(cls.parse_entity(text, match))
            raw_ix = max(raw_ix, match.end())
        if (raw_after := entity.Raw.from_slice(text, raw_ix, end)) is not None:
            content.append(raw_after)
        return content


class HashHeaderRule(Rule):
    pattern = re.compile(r"(?P<pre>^|\n)(?P<level>#{1,6})\s*(?P<text>.+)")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return entity.HeaderEntity(
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
        return entity.HeaderEntity(
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
        return entity.HeaderEntity(
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
    def __init_subclass__(cls, /, list_entity, item_pat, **kwargs):
        cls.list_entity = list_entity
        cls.item_pattern = re.compile(item_pat)
        cls.pattern = re.compile("\n" + item_pat + "+\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        list_el = cls.list_entity(text, m.start(), m.end(), [])
        matches = cls.item_pattern.finditer(text, m.start(), m.end())
        curr_indent = 0
        lists = [list_el]
        for match in matches:
            ind = parse_indent(match.group("indent"))
            li = entity.ListItemEntity(
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


class OlRule(
    ListLikeRule,
    list_entity=entity.OrderedListEntity,
    item_pat=r"(\n(?P<indent>(\t| {4,}))?\d+\.[\t ]+(?P<text>.+))",
):
    pass


class UlRule(
    ListLikeRule,
    list_entity=entity.UnorderedListEntity,
    item_pat=r"(\n(?P<indent>(\t| {4,}))?[-*+][\t ]+(?P<text>.+))",
):
    pass


class FencedPreRule(Rule):
    pattern = re.compile(r"\n(```|~~~)(?P<lang>\w+)?\n(?P<text>(.|\n)+)\1\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return entity.FencedPreEntity(
            text, m.start(), m.end(), m.group("lang"), m.group("text")
        )


class IndentedPreRule(Rule):
    LINE_PAT = r"(\n(\t| {4,})(?P<text>.+))"
    line_pattern = re.compile(LINE_PAT)
    pattern = re.compile("\n" + LINE_PAT + "+\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        outer_el = entity.IndentedPreEntity(text, m.start(), m.end())
        matches = cls.line_pattern.finditer(text, m.start(), m.end())
        for match in matches:
            outer_el.push_line(
                entity.IndentedPreLineEntity(
                    text, match.start("text"), match.end("text")
                )
            )
        return outer_el


class BlockQuoteRule(Rule):
    LINE_PAT = r"(\n>( (?P<text>.+))?)"
    line_pattern = re.compile(LINE_PAT)
    pattern = re.compile("\n" + LINE_PAT + "+\n")

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        outer_el = entity.BlockQuoteEntity(text, m.start(), m.end())
        matches = cls.line_pattern.finditer(text, m.start(), m.end())
        for match in matches:
            if match.group("text"):
                start = match.start("text")
                end = match.end("text")
            else:
                start = match.end()
                end = match.end()
            outer_el.push_line(entity.BlockQuoteLineEntity(text, start, end))
        return outer_el


class SimpleWrappingRule(Rule):
    delimiter: str
    entity: Entity

    @classmethod
    def __init_subclass__(cls, /, delimiter, entity, **kwargs):
        pat_str = f"({delimiter})(?P<text>.+)(\\1)"
        cls.pattern = re.compile(pat_str)
        cls.entity = entity

    @classmethod
    def parse_entity(cls, text: str, m: re.Match) -> Entity:
        return cls.entity(
            text,
            m.start(),
            m.end(),
            Content.raw_remainder(text, m.start("text"), m.end("text")),
        )


class EmRule(SimpleWrappingRule, delimiter="[*_]", entity=entity.EmEntity):
    pass


class BoldRule(SimpleWrappingRule, delimiter="[*_]{2}", entity=entity.BoldEntity):
    pass


class BoldEmRule(SimpleWrappingRule, delimiter="[*_]{3}", entity=entity.BoldEmEntity):
    pass


def parse_indent(indent: str | None) -> int:
    if indent is None:
        return 0
    return len(indent.replace("\t", "  ")) // 2
