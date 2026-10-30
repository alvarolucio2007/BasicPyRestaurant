from domain.category import Category
from mongodb.category_repository import CategoryRepository


class CategoryNotFound(Exception): ...
class CategoryValidationError(Exception): ...

class CategoryService:
    def __init__(self,repo:CategoryRepository) -> None:
        self.repo=repo
    def create(self,*,name:str,display_order:int)->Category:
        if not name or not name.strip():
            raise CategoryValidationError("Name is missing!")
        if not display_order or display_order<=0:
            raise CategoryValidationError("Display order is either missing or invalid! Please try again with a value greater than 0.")
        return self.repo.add(Category(name=name,display_order=display_order,category_id=None))
    def fetch_by_id(self,*,id:str)->Category|None:
        if not id or not id.strip():
            raise ValueError("ID is missing!")
        return self.repo.fetch_by_id(id=id)
    def update(self,*,category:Category)->Category:
        if not category.category_id:
            raise CategoryValidationError("ID is missing!")
        if not category.name or not category.name.strip():
            raise CategoryValidationError("Name is missing!")
        if category.display_order is None or category.display_order <= 0:
            raise CategoryValidationError("Order must be greater than 0.")
        ok = self.repo.update(category=category)
        if not ok:
            raise CategoryNotFound(category.category_id)
        return category
    def delete(self,*,category_id:str)->None:
        if not category_id or not category_id.strip():
            raise CategoryValidationError("ID is missing!")
        ok = self.repo.delete(id=category_id)
        if not ok:
            raise CategoryNotFound(category_id)
