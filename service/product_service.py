
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
            raise ProductValidationError("Nome é obrigatório.")
        if not description or not description.strip():
            raise ProductValidationError("Descrição é obrigatória.")
        if price is None or price <= 0:
            raise ProductValidationError("Preço deve ser maior que zero.")
        if not category_id or not category_id.strip():
            raise ProductValidationError("Categoria é obrigatória.")
        return self.repo.add(Product(
            name=name.strip(),
            description=description.strip(),
            price=price,
            category_id=category_id,
            available=available,
        ))

    def fetch_by_id(self, *, product_id: str) -> Product:
        if not product_id or not product_id.strip():
            raise ProductValidationError("ID é obrigatório.")
        product = self.repo.fetch_by_id(id=product_id)
        if product is None:
            raise ProductNotFound(product_id)
        return product

    def list_all(self) -> list[Product]:
        return self.repo.list_all()

    def list_by_category(self, *, category_id: str) -> list[Product]:
        if not category_id or not category_id.strip():
            raise ProductValidationError("ID da categoria é obrigatório.")
        return self.repo.list_by_category(category_id=category_id)

    def list_available(self) -> list[Product]:
        return self.repo.list_available()

    def update(self, *, product: Product) -> Product:
        if not product.product_id or not product.product_id.strip():
            raise ProductValidationError("ID do produto é obrigatório.")
        if not product.name or not product.name.strip():
            raise ProductValidationError("Nome é obrigatório.")
        if not product.description or not product.description.strip():
            raise ProductValidationError("Descrição é obrigatória.")
        if product.price is None or product.price <= 0:
            raise ProductValidationError("Preço deve ser maior que zero.")
        if not product.category_id or not product.category_id.strip():
            raise ProductValidationError("Categoria é obrigatória.")

        product.name = product.name.strip()
        product.description = product.description.strip()

        ok = self.repo.update(product=product)
        if not ok:
            raise ProductNotFound(product.product_id)
        return product

    def delete(self, *, product_id: str) -> None:
        if not product_id or not product_id.strip():
            raise ProductValidationError("ID é obrigatório.")
        ok = self.repo.delete(id=product_id)
        if not ok:
            raise ProductNotFound(product_id)
