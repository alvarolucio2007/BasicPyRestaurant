
from domain.product import Product
from mongodb.product_repository import ProductRepository


class ProductNotFound(Exception):...
class ProductValidationError(Exception):...

class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self.repo = repo

    def create(self, *, name: str, description: str, price: float,
               category_id: str, available: bool = True) -> Product:
        if not name or not name.strip():
            raise ProductValidationError("Name is missing.")
        if not description or not description.strip():
            raise ProductValidationError("Description is missing.")
        if price is None or price <= 0:
            raise ProductValidationError("Price must be greater than 0.")
        if not category_id or not category_id.strip():
            raise ProductValidationError("Category is missing.")
        return self.repo.add(Product(
            name=name.strip(),
            description=description.strip(),
            price=price,
            category_id=category_id,
            available=available,
        ))

    def fetch_by_id(self, *, product_id: str) -> Product:
        if not product_id or not product_id.strip():
            raise ProductValidationError("ID is missing.")
        product = self.repo.fetch_by_id(id=product_id)
        if product is None:
            raise ProductNotFound(product_id)
        return product

    def list_all(self) -> list[Product]:
        return self.repo.list_all()

    def list_by_category(self, *, category_id: str) -> list[Product]:
        if not category_id or not category_id.strip():
            raise ProductValidationError("Category ID is missing.")
        return self.repo.list_by_category(category_id=category_id)

    def list_available(self) -> list[Product]:
        return self.repo.list_available()

    def update(self, *, product: Product) -> Product:
        if not product.product_id or not product.product_id.strip():
            raise ProductValidationError("ID is missing.")
        if not product.name or not product.name.strip():
            raise ProductValidationError("Name is missing.")
        if not product.description or not product.description.strip():
            raise ProductValidationError("Description is missing.")
        if product.price is None or product.price <= 0:
            raise ProductValidationError("Price must be greater than 0.")
        if not product.category_id or not product.category_id.strip():
            raise ProductValidationError("Category is missing.")

        product.name = product.name.strip()
        product.description = product.description.strip()

        ok = self.repo.update(product=product)
        if not ok:
            raise ProductNotFound(product.product_id)
        return product

    def delete(self, *, product_id: str) -> None:
        if not product_id or not product_id.strip():
            raise ProductValidationError("ID is missing.")
        ok = self.repo.delete(id=product_id)
        if not ok:
            raise ProductNotFound(product_id)
