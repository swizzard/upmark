from .entity import Content
from .rule import Rule


class Parser:
    blocks: [Rule]
    # finalizer: Callable[[Raw], Content]

    def __init__(self, blocks: [Rule], finalizer=None):
        self.blocks = blocks

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
