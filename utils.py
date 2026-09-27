# Размерные сетки для конвертера обуви
# Базовая стандартная сетка размеров обуви (Мужская и Женская)

SHOE_SIZE_CHART = {
    "man": [
        {"us": 7.0, "uk": 6.5, "rus": 39.0, "eur": 40.0, "cm": 25.0},
        {"us": 7.5, "uk": 7.0, "rus": 39.5, "eur": 40.5, "cm": 25.5},
        {"us": 8.0, "uk": 7.5, "rus": 40.0, "eur": 41.0, "cm": 26.0},
        {"us": 8.5, "uk": 8.0, "rus": 41.0, "eur": 42.0, "cm": 26.5},
        {"us": 9.0, "uk": 8.5, "rus": 41.5, "eur": 42.5, "cm": 27.0},
        {"us": 9.5, "uk": 9.0, "rus": 42.0, "eur": 43.0, "cm": 27.5},
        {"us": 10.0, "uk": 9.5, "rus": 42.5, "eur": 44.0, "cm": 28.0},
        {"us": 10.5, "uk": 10.0, "rus": 43.0, "eur": 44.5, "cm": 28.5},
        {"us": 11.0, "uk": 10.5, "rus": 43.5, "eur": 45.0, "cm": 29.0},
        {"us": 11.5, "uk": 11.0, "rus": 44.0, "eur": 45.5, "cm": 29.5},
        {"us": 12.0, "uk": 11.5, "rus": 44.5, "eur": 46.0, "cm": 30.0},
        {"us": 12.5, "uk": 12.0, "rus": 45.0, "eur": 47.0, "cm": 30.5},
        {"us": 13.0, "uk": 12.5, "rus": 46.0, "eur": 47.5, "cm": 31.0},
    ],
    "woman": [
        {"us": 5.0, "uk": 3.0, "rus": 35.0, "eur": 35.5, "cm": 22.0},
        {"us": 5.5, "uk": 3.5, "rus": 35.5, "eur": 36.0, "cm": 22.5},
        {"us": 6.0, "uk": 4.0, "rus": 36.0, "eur": 36.5, "cm": 23.0},
        {"us": 6.5, "uk": 4.5, "rus": 36.5, "eur": 37.5, "cm": 23.5},
        {"us": 7.0, "uk": 5.0, "rus": 37.0, "eur": 38.0, "cm": 24.0},
        {"us": 7.5, "uk": 5.5, "rus": 37.5, "eur": 38.5, "cm": 24.5},
        {"us": 8.0, "uk": 6.0, "rus": 38.0, "eur": 39.0, "cm": 25.0},
        {"us": 8.5, "uk": 6.5, "rus": 38.5, "eur": 40.0, "cm": 25.5},
        {"us": 9.0, "uk": 7.0, "rus": 39.0, "eur": 40.5, "cm": 26.0},
        {"us": 9.5, "uk": 7.5, "rus": 40.0, "eur": 41.0, "cm": 26.5},
        {"us": 10.0, "uk": 8.0, "rus": 40.5, "eur": 42.0, "cm": 27.0},
    ]
}

def calculate_hr_zones(hr_max: int):
    """
    Расчёт 5 пульсовых зон на основе ЧСС max:
    Zone 1: 60-70%
    Zone 2: 70-75%
    Zone 3: 75-85%
    Zone 4: 85-95%
    Zone 5: 95-100%
    """
    return [
        {
            "zone": 1,
            "name": "Zone 1: Медленный бег",
            "min": round(hr_max * 0.60),
            "max": round(hr_max * 0.70),
            "target": round(hr_max * 0.69),
            "color": "#5bc0de"
        },
        {
            "zone": 2,
            "name": "Zone 2: Легкий темп",
            "min": round(hr_max * 0.70),
            "max": round(hr_max * 0.75),
            "target": round(hr_max * 0.74),
            "color": "#5cb85c"
        },
        {
            "zone": 3,
            "name": "Zone 3: Темповой бег",
            "min": round(hr_max * 0.75),
            "max": round(hr_max * 0.85),
            "target": round(hr_max * 0.83),
            "color": "#f0ad4e"
        },
        {
            "zone": 4,
            "name": "Zone 4: Бег на уровне ПАНО",
            "min": round(hr_max * 0.85),
            "max": round(hr_max * 0.95),
            "target": round(hr_max * 0.92),
            "color": "#f0803c"
        },
        {
            "zone": 5,
            "name": "Zone 5: Бег в зоне МПК",
            "min": round(hr_max * 0.95),
            "max": hr_max,
            "target": round(hr_max * 0.97),
            "color": "#d9534f"
        }
    ]
