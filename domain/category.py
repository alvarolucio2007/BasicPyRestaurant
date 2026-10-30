from dataclasses import dataclass


@dataclass
class Category:
    name: str
    display_order:int
    category_id:str|None
