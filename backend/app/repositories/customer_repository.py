from backend.app.schemas.customer import CustomerProfile


class CustomerRepository:
    def __init__(self) -> None:
        self._customers: dict[str, CustomerProfile] = {}

    def save(self, customer: CustomerProfile) -> CustomerProfile:
        self._customers[customer.customer_id] = customer
        return customer

    def get(self, customer_id: str) -> CustomerProfile | None:
        return self._customers.get(customer_id)

