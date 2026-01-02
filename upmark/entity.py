from typing import Self


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
        return f'Raw(start={self.start}, end={self.end}, text="{repr(self.text[self.start : min(self.end, self.start + 10)])}...")'


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

    def __eq__(self, other):
        return (
            isinstance(other, HeaderEntity)
            and other.is_bof == self.is_bof
            and other.start == self.start
            and other.end == self.end
            and other.level == self.level
            and self.text == other.text
            and self.content == other.content
        )


class ListItemEntity(WrappingBlockEntity):
    tag = "li"


class ListEntity(Entity):
    content: [ListItemEntity | Self]
    tag: str

    def __init__(self, text, start, end, content: [ListItemEntity | Self]):
        super().__init__(text, start, end)
        self.content = content

    def push_item(self, item: ListItemEntity | Self):
        self.content.append(item)

    def trim_to_content(self):
        last_item = self.content[-1]
        if isinstance(last_item, ListEntity):
            last_item.trim_to_content()
        self.end = last_item.end

    def to_string(self):
        return f"\n<{self.tag}>{''.join(entity.to_string() for entity in self.content)}</{self.tag}>\n"

    def __eq__(self, other):
        return (
            isinstance(other, ListEntity)
            and other.start == self.start
            and other.end == self.end
            and other.tag == self.tag
            and other.content == self.content
        )


class OrderedListEntity(ListEntity):
    tag = "ol"


class UnorderedListEntity(ListEntity):
    tag = "ul"
