
import random
def define_u(type_ground: int, pressure_array: list):
    u_from_ground_type = {
        1: random.uniform(0.9, 0.96),  # Песок гравелистый
        2: random.uniform(0.9, 0.96),  # Песок крупный
        3: random.uniform(0.9, 0.96),  # Песок средней крупности
        4: random.uniform(0.9, 0.96),  # Песок мелкий
        5: random.uniform(0.9, 0.96),  # Песок пылеватый
        6: random.uniform(0.9, 0.96),  # Супесь
        7: random.uniform(0.9, 0.96),  # Суглинок
        8: random.uniform(0.9, 0.96),  # Глина
        9: random.uniform(0.9, 0.96),  # Торф
    }

    u = [round(u_from_ground_type[type_ground] * pressure, 1) for pressure in pressure_array]

    return u

array = [0, 0, 200, 300]

array = list(filter(lambda pressure: pressure != 0, array))



print(array)

#print(define_u(1, [100, 200, 300]))

