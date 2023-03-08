import enum


class NewBuyStep(enum.Enum):
    amount_payment = 'amount_payment'
    wrong_amount = 'wrong_amount'
    purchase_name = 'purchase_name'
    category = 'category'
