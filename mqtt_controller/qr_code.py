import pay_by_square
import requests


def eur_code(amount: str, message: str = "") -> str:
    code = pay_by_square.generate(
        amount=float(amount),
        iban="SK4583300000002100288485",
        swift="FIOZSKBAXXX",
        note=message,
    )
    return code


def cz_code(amount: str, message: str = "") -> str:
    url = f"http://api.paylibo.com/paylibo/generator/czech/string?accountNumber=2100288506&bankCode=2010&amount={amount}&message={message}"
    return requests.get(url).text
