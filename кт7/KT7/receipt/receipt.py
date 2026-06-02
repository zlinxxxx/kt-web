from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class PaymentMethod(Enum):
    CASH = "Наличные"
    CARD = "Безналичный расчёт"
    QR = "СБП"


@dataclass
class ServiceItem:
    name: str
    quantity: int
    price: float

    @property
    def total(self) -> float:
        return round(self.quantity * self.price, 2)


class Receipt:
    ORG_NAME = 'СПОРТИВНЫЙ КОМПЛЕКС "ОЛИМПИЯ"'
    LINE_WIDTH = 41

    def __init__(
        self,
        discount_percent: float = 0,
        vat_percent: float = 20,
        payment_method: PaymentMethod = PaymentMethod.CARD,
        receipt_number: Optional[int] = None,
        date: Optional[datetime] = None,
    ) -> None:
        self.discount_percent = discount_percent
        self.vat_percent = vat_percent
        self.payment_method = payment_method
        self.receipt_number = receipt_number if receipt_number is not None else 1
        self.date = date if date is not None else datetime.now()
        self.items: list[ServiceItem] = []

    def add_item(self, item: ServiceItem) -> None:
        if item.price < 0:
            raise ValueError("Цена не может быть отрицательной")
        if item.quantity <= 0:
            raise ValueError("Количество должно быть положительным")
        self.items.append(item)

    def _validate(self) -> None:
        if not self.items:
            raise ValueError("Корзина пуста")
        if self.discount_percent < 0 or self.discount_percent > 50:
            raise ValueError("Недопустимая скидка")
        if self.vat_percent < 0 or self.vat_percent > 100:
            raise ValueError("Недопустимый НДС")
        for item in self.items:
            if item.price < 0:
                raise ValueError("Цена не может быть отрицательной")
            if item.quantity <= 0:
                raise ValueError("Количество должно быть положительным")

    def calculate(self) -> dict:
        self._validate()
        subtotal = round(sum(item.total for item in self.items), 2)
        discount_amount = round(subtotal * self.discount_percent / 100, 2)
        total_without_vat = round(subtotal - discount_amount, 2)
        vat_amount = round(total_without_vat * self.vat_percent / 100, 2)
        total = round(total_without_vat + vat_amount, 2)
        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "total_without_vat": total_without_vat,
            "vat_amount": vat_amount,
            "total": total,
        }

    def render(self) -> str:
        totals = self.calculate()
        sep = "-" * self.LINE_WIDTH
        dsep = "=" * self.LINE_WIDTH

        lines: list[str] = []
        lines.append(self.ORG_NAME)
        date_str = self.date.strftime("%d.%m.%Y %H:%M")
        lines.append(f"Дата: {date_str}    Чек №: {self.receipt_number:04d}")
        lines.append(sep)
        lines.append(f"{'Услуга':<22}{'Кол-во':>7}{'Цена':>7}{'Сумма':>9}")

        for item in self.items:
            name = item.name if len(item.name) <= 22 else item.name[:19] + "..."
            qty = str(item.quantity)
            price = self._fmt_num(item.price)
            total = self._fmt_num(item.total)
            lines.append(f"{name:<22}{qty:>7}{price:>7}{total:>9}")

        lines.append(sep)
        lines.append(self._right_label("Подытог:", self._fmt_num(totals["subtotal"])))

        if self.discount_percent > 0:
            lines.append(
                self._right_label(
                    f"Скидка ({self._fmt_percent(self.discount_percent)}%):",
                    "-" + self._fmt_num(totals["discount_amount"]),
                )
            )

        if self.vat_percent > 0:
            lines.append(
                self._right_label(
                    "Итого без НДС:", self._fmt_num(totals["total_without_vat"])
                )
            )
            lines.append(
                self._right_label(
                    f"НДС ({self._fmt_percent(self.vat_percent)}%):",
                    self._fmt_num(totals["vat_amount"]),
                )
            )

        lines.append(dsep)
        lines.append(self._right_label("К ОПЛАТЕ:", f"{totals['total']:.2f} ₽"))
        lines.append(f"Способ оплаты: {self.payment_method.value}")
        lines.append("Спасибо за визит!")
        lines.append(dsep)

        return "\n".join(lines)

    @staticmethod
    def _fmt_num(value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:.2f}"

    @staticmethod
    def _fmt_percent(value: float) -> str:
        if float(value).is_integer():
            return str(int(value))
        return f"{value:g}"

    def _right_label(self, label: str, value: str) -> str:
        space = self.LINE_WIDTH - len(label) - len(value)
        if space < 1:
            space = 1
        return f"{label}{' ' * space}{value}"
