from datetime import datetime

import allure
import pytest

from receipt import PaymentMethod, Receipt, ServiceItem


@allure.feature("Кассовый модуль")
@allure.story("Расчёт стоимости")
@allure.severity(allure.severity_level.CRITICAL)
class TestCalculation:
    @allure.title("Расчёт итогов: {case_id}")
    @pytest.mark.parametrize(
        "case_id, items, discount, vat, expected",
        [
            (
                "без скидки, НДС 20%",
                [("Бассейн", 2, 500.0)],
                0,
                20,
                {
                    "subtotal": 1000.0,
                    "discount_amount": 0.0,
                    "total_without_vat": 1000.0,
                    "vat_amount": 200.0,
                    "total": 1200.0,
                },
            ),
            (
                "скидка 10%, НДС 20%",
                [("Бассейн", 2, 500.0), ("Аренда шкафчика", 1, 150.0)],
                10,
                20,
                {
                    "subtotal": 1150.0,
                    "discount_amount": 115.0,
                    "total_without_vat": 1035.0,
                    "vat_amount": 207.0,
                    "total": 1242.0,
                },
            ),
            (
                "скидка 50%, НДС 20%",
                [("Тренажёрный зал", 4, 300.0)],
                50,
                20,
                {
                    "subtotal": 1200.0,
                    "discount_amount": 600.0,
                    "total_without_vat": 600.0,
                    "vat_amount": 120.0,
                    "total": 720.0,
                },
            ),
            (
                "без скидки, НДС 0%",
                [("Групповые занятия", 3, 400.0)],
                0,
                0,
                {
                    "subtotal": 1200.0,
                    "discount_amount": 0.0,
                    "total_without_vat": 1200.0,
                    "vat_amount": 0.0,
                    "total": 1200.0,
                },
            ),
            (
                "скидка 20%, НДС 20%",
                [("Персональная тренировка", 1, 2000.0)],
                20,
                20,
                {
                    "subtotal": 2000.0,
                    "discount_amount": 400.0,
                    "total_without_vat": 1600.0,
                    "vat_amount": 320.0,
                    "total": 1920.0,
                },
            ),
        ],
    )
    def test_calculate_totals(self, case_id, items, discount, vat, expected):
        receipt = Receipt(discount_percent=discount, vat_percent=vat)
        with allure.step("Добавление услуги"):
            for name, qty, price in items:
                receipt.add_item(ServiceItem(name=name, quantity=qty, price=price))

        with allure.step("Расчёт итога"):
            result = receipt.calculate()

        assert result == expected


@allure.feature("Кассовый модуль")
@allure.story("Валидация")
@allure.severity(allure.severity_level.NORMAL)
class TestValidation:
    @allure.title("Отрицательная цена услуги бросает ValueError")
    def test_negative_price(self):
        receipt = Receipt()
        with pytest.raises(ValueError, match="Цена не может быть отрицательной"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=-100.0))

    @allure.title("Нулевое количество бросает ValueError")
    def test_zero_quantity(self):
        receipt = Receipt()
        with pytest.raises(ValueError, match="Количество должно быть положительным"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=0, price=500.0))

    @allure.title("Отрицательное количество бросает ValueError")
    def test_negative_quantity(self):
        receipt = Receipt()
        with pytest.raises(ValueError, match="Количество должно быть положительным"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=-1, price=500.0))

    @allure.title("Пустая корзина при расчёте бросает ValueError")
    def test_empty_cart_calculate(self):
        receipt = Receipt()
        with pytest.raises(ValueError, match="Корзина пуста"):
            receipt.calculate()

    @allure.title("Пустая корзина при render() бросает ValueError")
    def test_empty_cart_render(self):
        receipt = Receipt()
        with pytest.raises(ValueError, match="Корзина пуста"):
            receipt.render()

    @allure.title("Скидка больше 50% недопустима")
    def test_discount_over_max(self):
        receipt = Receipt(discount_percent=51)
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=500.0))
        with pytest.raises(ValueError, match="Недопустимая скидка"):
            receipt.calculate()

    @allure.title("Отрицательная скидка недопустима")
    def test_discount_negative(self):
        receipt = Receipt(discount_percent=-5)
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=500.0))
        with pytest.raises(ValueError, match="Недопустимая скидка"):
            receipt.calculate()

    @allure.title("Недопустимый НДС бросает ValueError")
    def test_invalid_vat(self):
        receipt = Receipt(vat_percent=150)
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=500.0))
        with pytest.raises(ValueError, match="Недопустимый НДС"):
            receipt.calculate()


@allure.feature("Кассовый модуль")
@allure.story("Расчёт стоимости")
@allure.severity(allure.severity_level.CRITICAL)
class TestPaymentMethods:
    @allure.title("Чек содержит способ оплаты: {method}")
    @pytest.mark.parametrize("method", list(PaymentMethod))
    def test_payment_method_in_receipt(self, method):
        receipt = Receipt(
            payment_method=method,
            receipt_number=42,
            date=datetime(2026, 1, 1, 12, 0),
        )
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=500.0))

        with allure.step("Расчёт итога"):
            rendered = receipt.render()

        assert f"Способ оплаты: {method.value}" in rendered
        allure.attach(
            rendered,
            name=f"Чек ({method.name})",
            attachment_type=allure.attachment_type.TEXT,
        )


@allure.feature("Кассовый модуль")
@allure.story("Расчёт стоимости")
@allure.severity(allure.severity_level.NORMAL)
class TestBoundary:
    @allure.title("Чек с одной услугой формируется корректно")
    def test_single_item(self):
        receipt = Receipt(
            receipt_number=1, date=datetime(2026, 1, 1, 10, 0)
        )
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=500.0))

        with allure.step("Расчёт итога"):
            rendered = receipt.render()

        assert "Бассейн" in rendered
        assert "К ОПЛАТЕ:" in rendered

    @allure.title("Максимальная скидка 50%")
    def test_max_discount(self):
        receipt = Receipt(discount_percent=50)
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=2, price=500.0))

        with allure.step("Расчёт итога"):
            result = receipt.calculate()

        assert result["discount_amount"] == 500.0
        assert result["total"] == 600.0

    @allure.title("НДС 0% — строка НДС отсутствует в чеке")
    def test_zero_vat(self):
        receipt = Receipt(
            vat_percent=0,
            receipt_number=2,
            date=datetime(2026, 1, 1, 10, 0),
        )
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=1, price=500.0))

        with allure.step("Расчёт итога"):
            rendered = receipt.render()

        assert "НДС" not in rendered
        assert "К ОПЛАТЕ:" in rendered
        allure.attach(
            rendered, name="Чек", attachment_type=allure.attachment_type.TEXT
        )

    @allure.title("Очень длинное название услуги (>30 символов) не ломает render()")
    def test_long_service_name(self):
        long_name = "Очень длинное название услуги спортивного комплекса премиум"
        assert len(long_name) > 30
        receipt = Receipt(
            receipt_number=3, date=datetime(2026, 1, 1, 10, 0)
        )
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name=long_name, quantity=1, price=1500.0))

        with allure.step("Расчёт итога"):
            rendered = receipt.render()

        assert "К ОПЛАТЕ:" in rendered

    @allure.title("Финальный чек с полным набором полей прикладывается в отчёт")
    def test_full_receipt_attached(self):
        receipt = Receipt(
            discount_percent=10,
            vat_percent=20,
            payment_method=PaymentMethod.CARD,
            receipt_number=1042,
            date=datetime(2026, 1, 15, 14, 30),
        )
        with allure.step("Добавление услуги"):
            receipt.add_item(ServiceItem(name="Бассейн", quantity=2, price=500.0))
            receipt.add_item(ServiceItem(name="Аренда шкафчика", quantity=1, price=150.0))

        with allure.step("Расчёт итога"):
            rendered = receipt.render()

        allure.attach(
            rendered, name="Чек", attachment_type=allure.attachment_type.TEXT
        )
        assert "К ОПЛАТЕ:" in rendered
        assert "1242.00" in rendered
