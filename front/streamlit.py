#Note: All the pyright comments are because of the X|None types, app should work as intended
import streamlit as st

from service.category_service import (
    CategoryNotFound,
    CategoryService,
    CategoryValidationError,
)
from service.order_service import (
    OrderService,
    OrderValidationError,
)
from service.product_service import (
    ProductNotFound,
    ProductService,
    ProductValidationError,
)


class Streamlit:
    def __init__(
        self,
        category_service: CategoryService,
        order_service: OrderService,
        product_service: ProductService,
    ) -> None:
        self.category_service = category_service
        self.order_service = order_service
        self.product_service = product_service

    def flash(self, message: str, kind: str = "success") -> None:
        st.session_state["flash"] = (kind, message)

    def show_flash(self) -> None:
        if "flash" in st.session_state:
            kind, message = st.session_state.pop("flash")
            getattr(st, kind)(message)

    def run(self) -> None:
        st.sidebar.title("🍽️ Restaurant Admin")
        page = st.sidebar.radio(
            "Navigation",
            ["🍔 Categories", "🍕 Products", "🧾 Orders"],
        )
        self.show_flash()

        if page == "🍔 Categories":
            self.page_categories()
        elif page == "🍕 Products":
            self.page_products()
        else:
            self.page_orders()

    def page_categories(self) -> None:
        st.header("Categories")

        with st.form("create_category", clear_on_submit=True):
            name = st.text_input("Name")
            display_order = st.number_input("Display order", min_value=1, step=1, value=1)
            if st.form_submit_button("Create category"):
                try:
                    self.category_service.create(
                        name=name, display_order=int(display_order),
                    )
                    self.flash(f"Category '{name}' created.")
                    st.rerun()
                except CategoryValidationError as e:
                    st.error(str(e))

        categories = self.category_service.list_all()
        if not categories:
            st.info("No categories yet.")
            return

        st.subheader("Existing categories")
        st.dataframe(
            [{"id": c.category_id, "name": c.name, "order": c.display_order}
             for c in categories],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Edit or delete")
        options = {f"{c.name} (#{c.display_order})": c for c in categories}
        choice = st.selectbox("Pick one", list(options.keys()))
        if not choice:
            return

        cat = options[choice]
        with st.form("edit_category"):
            new_name = st.text_input("Name", value=cat.name)
            new_order = st.number_input(
                "Display order", min_value=1, step=1, value=cat.display_order,
            )
            col1, col2 = st.columns(2)
            save = col1.form_submit_button("💾 Save")
            delete = col2.form_submit_button("🗑️ Delete")

        if save:
            try:
                cat.name = new_name.strip()
                cat.display_order = int(new_order)
                self.category_service.update(category=cat)
                self.flash("Category updated.")
                st.rerun()
            except CategoryValidationError as e:
                st.error(str(e))
            except CategoryNotFound:
                self.flash("Category no longer exists.", "error")
                st.rerun()

        if delete:
            try:
                self.category_service.delete(category_id=cat.category_id)  # pyright: ignore[reportArgumentType]
                self.flash("Category deleted.")
                st.rerun()
            except CategoryNotFound:
                self.flash("Category no longer exists.", "error")
                st.rerun()

    def page_products(self) -> None:
        st.header("Products")

        categories = self.category_service.list_all()
        if not categories:
            st.warning("Create a category first.")
            return

        cat_options = {c.name: c.category_id for c in categories}

        with st.form("create_product", clear_on_submit=True):
            name = st.text_input("Name")
            description = st.text_area("Description")
            price = st.number_input("Price (R$)", min_value=0.01, step=0.50, format="%.2f")
            cat_name = st.selectbox("Category", list(cat_options.keys()))
            available = st.checkbox("Available", value=True)
            if st.form_submit_button("Create product"):
                try:
                    self.product_service.create(
                        name=name,
                        description=description,
                        price=float(price),
                        category_id=cat_options[cat_name],  # pyright: ignore[reportArgumentType]
                        available=available,
                    )
                    self.flash(f"Product '{name}' created.")
                    st.rerun()
                except ProductValidationError as e:
                    st.error(str(e))

        products = self.product_service.list_all()
        if not products:
            st.info("No products yet.")
            return

        st.subheader("Menu")
        cat_map = {c.category_id: c.name for c in categories}
        st.dataframe(
            [{
                "name": p.name,
                "category": cat_map.get(p.category_id, "—"),
                "price": f"R$ {p.price:.2f}",
                "available": "✅" if p.available else "❌",
            } for p in products],
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Edit or delete")
        options = {f"{p.name} — R$ {p.price:.2f}": p for p in products}
        choice = st.selectbox("Pick one", list(options.keys()))
        if not choice:
            return

        prod = options[choice]
        with st.form("edit_product"):
            new_name = st.text_input("Name", value=prod.name)
            new_desc = st.text_area("Description", value=prod.description)
            new_price = st.number_input(
                "Price (R$)", min_value=0.01, step=0.50,
                value=float(prod.price), format="%.2f",
            )
            cat_names = list(cat_options.keys())
            cur_idx = cat_names.index(
                next(n for n, i in cat_options.items() if i == prod.category_id)
            ) if prod.category_id in cat_options.values() else 0
            new_cat_name = st.selectbox("Category", cat_names, index=cur_idx)
            new_available = st.checkbox("Available", value=prod.available)
            col1, col2 = st.columns(2)
            save = col1.form_submit_button("💾 Save")
            delete = col2.form_submit_button("🗑️ Delete")

        if save:
            try:
                prod.name = new_name.strip()
                prod.description = new_desc.strip()
                prod.price = float(new_price)
                prod.category_id = cat_options[new_cat_name]  # pyright: ignore[reportAttributeAccessIssue]
                prod.available = new_available
                self.product_service.update(product=prod)
                self.flash("Product updated.")
                st.rerun()
            except ProductValidationError as e:
                st.error(str(e))
            except ProductNotFound:
                self.flash("Product no longer exists.", "error")
                st.rerun()

        if delete:
            try:
                self.product_service.delete(product_id=prod.product_id)  # pyright: ignore[reportArgumentType]
                self.flash("Product deleted.")
                st.rerun()
            except ProductNotFound:
                self.flash("Product no longer exists.", "error")
                st.rerun()

    def page_orders(self) -> None:
        st.header("Orders")

        available = self.product_service.list_available()
        if not available:
            st.warning("No available products to order.")
        else:
            prod_map = {f"{p.name} — R$ {p.price:.2f}": p for p in available}

            with st.form("create_order", clear_on_submit=True):
                table = st.number_input("Table number", min_value=1, step=1, value=1)
                customer = st.text_input("Customer name")
                chosen = st.multiselect("Products", list(prod_map.keys()))

                quantities = {}
                for label in chosen:
                    quantities[label] = st.number_input(
                        f"Qty — {label}", min_value=1, step=1, value=1, key=f"qty_{label}",
                    )

                if st.form_submit_button("Place order"):
                    try:
                        items = [
                            self.order_service.create_order_item(
                                product_id=prod_map[label].product_id,  # pyright: ignore[reportArgumentType]
                                product_name=prod_map[label].name,
                                unit_price=prod_map[label].price,
                                quantity=int(quantities[label]),
                            )
                            for label in chosen
                        ]
                        order = self.order_service.create(
                            table_number=int(table),
                            customer_name=customer,
                            items=items,
                        )
                        self.flash(f"Order #{order.order_id} created — total R$ {order.total_amount:.2f}.")
                        st.rerun()
                    except OrderValidationError as e:
                        st.error(str(e))

        st.subheader("Active orders")
        for status in ("pending", "preparing", "delivered"):
            orders = self.order_service.list_by_status(status=status)
            if not orders:
                continue
            st.markdown(f"### {status.capitalize()}")
            for o in orders:
                with st.expander(f"Order #{o.order_id} — Table {o.table_number} — R$ {o.total_amount:.2f}"):
                    st.write(f"**Customer:** {o.customer_name}")
                    st.write(f"**Created at:** {o.created_at}")
                    st.table([{
                        "item": i.product_name,
                        "qty": i.quantity,
                        "unit": f"R$ {i.unit_price:.2f}",
                        "subtotal": f"R$ {i.subtotal:.2f}",
                        "notes": i.notes or "—",
                    } for i in o.items])

                    if status not in ("delivered",):
                        next_status = {"pending": "preparing", "preparing": "delivered"}[status]
                        if st.button(f"Advance to '{next_status}'", key=f"adv_{o.order_id}"):
                            try:
                                self.order_service.update_status(
                                    order_id=o.order_id, status=next_status,  # pyright: ignore[reportArgumentType]
                                )
                                self.flash(f"Order #{o.order_id} → {next_status}.")
                                st.rerun()
                            except OrderValidationError as e:
                                st.error(str(e))
