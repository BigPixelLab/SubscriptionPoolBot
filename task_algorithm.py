import random

def lottery_prizes_generator(num_clients, prizes):
    # Проверка на наличие призов
    if not prizes:
        raise ValueError("Список призов пуст")

    # Распределение призов по категориям (count и weight)
    count_prizes = []
    weight_prizes = []
    total_count = 0
    total_weight = 0

    for prize_id, prize_info in prizes.items():
        print(f'prize_id={prize_id} prize_info={prize_info}')
        if "count" in prize_info:
            count_prizes.extend([prize_id] * prize_info["count"])
            total_count += prize_info["count"]
        elif "weight" in prize_info:
            weight_prizes.extend([prize_id] * prize_info["weight"])
            total_weight += prize_info["weight"]
        # else:
            # del prizes[f'{prize_id}']

    # Проверка на наличие достаточного числа призов для всех клиентов
    if total_count > num_clients:
        raise ValueError("Не хватает призов для всех клиентов")

    while num_clients > 0:
        if count_prizes and random.random() < total_count / (total_count + total_weight):
            # Выбор приза на основе count
            selected_prize = random.choice(count_prizes)
            yield selected_prize
            count_prizes.remove(selected_prize)
            total_count -= 1
            num_clients -= 1
        elif weight_prizes:
            # Выбор приза на основе weight
            selected_prize = random.choice(weight_prizes)
            yield selected_prize
            weight_prizes.remove(selected_prize)
            total_weight -= 1
            num_clients -= 1

# Пример использования функции-генератора
clients = 20
prizes = {
    "000": {"coupon_type_id": "A", "weight": 3},
    "xxx": {"coupon_type_id": "A", "weight": 100},
    "001": {"coupon_type_id": "B", "count": 3},
    "002": {"coupon_type_id": "B", "count": 5},
    "003": {"coupon_type_id": "C"},  # Приз без weight и count
    "004": {"coupon_type_id": "D"},  # Приз без weight и count
    "005": {"coupon_type_id": "D"},  # Приз без weight и count

}

gen = lottery_prizes_generator(clients, prizes)
for i, prize in enumerate(gen, start=1):
    print(f"Client {i}: {prize}")
