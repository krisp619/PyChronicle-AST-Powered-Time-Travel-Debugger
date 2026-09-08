def calculate_total(price, quantity):
    total = price * quantity
    discount = 10
    final_price = total - discount
    return final_price


result = calculate_total(100, 2)
print(result)