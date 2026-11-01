from domain.category import Category
from service.category_service import CategoryService

class CategoryStreamlit:
    def __init__(self,service:CategoryService) -> None:
        self.service=CategoryService
