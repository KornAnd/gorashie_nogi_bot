# Текстовые калькуляторы и утилиты без сторонних серверов и веб-интерфейса

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

def format_hr_zones_text(hr_max: int) -> str:
    z1_min, z1_max = round(hr_max * 0.60), round(hr_max * 0.70)
    z2_min, z2_max = round(hr_max * 0.70), round(hr_max * 0.75)
    z3_min, z3_max = round(hr_max * 0.75), round(hr_max * 0.85)
    z4_min, z4_max = round(hr_max * 0.85), round(hr_max * 0.95)
    z5_min, z5_max = round(hr_max * 0.95), hr_max

    return (
        f"💓 **Пульсовые зоны для ЧСС max = {hr_max} уд/мин**:\n\n"
        f"🟦 **Zone 1 (Медленный бег)**: {z1_min}–{z1_max} уд/мин (Цель: {round(hr_max*0.69)})\n"
        f"🟩 **Zone 2 (Легкий темп)**: {z2_min}–{z2_max} уд/мин (Цель: {round(hr_max*0.74)})\n"
        f"🟨 **Zone 3 (Темповой бег)**: {z3_min}–{z3_max} уд/мин (Цель: {round(hr_max*0.83)})\n"
        f"🟧 **Zone 4 (Бег ПАНО)**: {z4_min}–{z4_max} уд/мин (Цель: {round(hr_max*0.92)})\n"
        f"🟥 **Zone 5 (Бег МПК)**: {z5_min}–{z5_max} уд/мин (Цель: {round(hr_max*0.97)})"
    )

def pace_to_speed_text(pace_str: str) -> str:
    try:
        parts = pace_str.split(':')
        mins = int(parts[0])
        secs = int(parts[1])
        total_hours = (mins * 60 + secs) / 3600
        if total_hours <= 0:
            return "Ошибка ввода."
        speed = round(1 / total_hours, 2)
        return f"⚡ Темп **{pace_str} мин/км** = **{speed} км/ч**"
    except Exception:
        return "⚠️ Введите темп в формате `МИН:СЕК`, например `05:30`"

def speed_to_pace_text(speed_val: float) -> str:
    try:
        if speed_val <= 0:
            return "Ошибка ввода."
        total_secs = round(3600 / speed_val)
        mins = total_secs // 60
        secs = total_secs % 60
        return f"⚡ Скорость **{speed_val} км/ч** = **{mins:02d}:{secs:02d} мин/км**"
    except Exception:
        return "⚠️ Введите числовую скорость, например `12.5`"
