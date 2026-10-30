from domain.category import Category
from mongodb.category_repository import CategoryRepository


class CategoryNotFound(Exception): ...
class CategoryValidationError(Exception): ...

class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo

    def create(self, *, name: str, display_order: int) -> Category:
        if not name or not name.strip():
            raise CategoryValidationError("Name is missing.")
        if display_order is None or display_order <= 0:
            raise CategoryValidationError("Order must be greater than 0.")
        return self.repo.add(category=Category(
            name=name.strip(),
            display_order=display_order,
            category_id=None,
        ))

    def fetch_by_id(self, *, category_id: str) -> Category:
        if not category_id or not category_id.strip():
            raise CategoryValidationError("ID is missing.")
        category = self.repo.fetch_by_id(id=category_id)
        if category is None:
            raise CategoryNotFound(category_id)
        return category

    def list_all(self) -> list[Category]:
        return self.repo.list_all()

    def update(self, *, category: Category) -> Category:
        if not category.category_id or not category.category_id.strip():
            raise CategoryValidationError("ID is missing.")
        if not category.name or not category.name.strip():
            raise CategoryValidationError("Name is missing.")
        if category.display_order is None or category.display_order <= 0:
            raise CategoryValidationError("Order must be greater than 0.")

        category.name = category.name.strip()

        ok = self.repo.update(category=category)
        if not ok:
            raise CategoryNotFound(category.category_id)
        return category

    def delete(self, *, category_id: str) -> None:
        if not category_id or not category_id.strip():
            raise CategoryValidationError("ID is missing.")
        ok = self.repo.delete(id=category_id)
        if not ok:
            raise CategoryNotFound(category_id)
