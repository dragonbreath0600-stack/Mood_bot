import pandas as pd
import matplotlib.pyplot as plt
import io


def weekly_stats(db, user_id):
    rows = db.get_entries(user_id, 7)
    return format_stats(rows, "За неделю")


def monthly_stats(db, user_id):
    rows = db.get_entries(user_id, 30)
    return format_stats(rows, "За месяц")


def insights(db, user_id):
    rows = db.get_entries(user_id, 30)
    if len(rows) < 3:
        return "Недостаточно данных для инсайтов. Записывай данные каждый день."

    good_mood = [r for r in rows if r[1] and r[1] >= 4]
    bad_mood = [r for r in rows if r[1] and r[1] <= 2]

    text = "Инсайты:\n\n"

    if good_mood:
        avg_sleep_good = sum(r[3] for r in good_mood if r[3]) / len([r for r in good_mood if r[3]] or [1])
        text += f"В дни с хорошим настроением ты спишь в среднем {avg_sleep_good:.1f}ч.\n"

    if bad_mood:
        avg_sleep_bad = sum(r[3] for r in bad_mood if r[3]) / len([r for r in bad_mood if r[3]] or [1])
        text += f"В дни с плохим настроением ты спишь в среднем {avg_sleep_bad:.1f}ч.\n"

    high_work = [r for r in rows if r[2] and r[2] >= 6]
    if high_work:
        avg_mood_busy = sum(r[1] for r in high_work if r[1]) / len([r for r in high_work if r[1]] or [1])
        text += f"В дни с 6+ часами работы среднее настроение: {avg_mood_busy:.1f}.\n"

    return text


def format_stats(rows, label):
    if not rows:
        return "Данных пока нет."
    moods = [r[1] for r in rows if r[1]]
    works = [r[2] for r in rows if r[2]]
    sleeps = [r[3] for r in rows if r[3]]
    text = f"{label} ({len(rows)} записей):\n\n"
    if moods:
        text += f"Среднее настроение: {sum(moods)/len(moods):.1f}\n"
    if works:
        text += f"Среднее часов работы: {sum(works)/len(works):.1f}\n"
    if sleeps:
        text += f"Среднее часов сна: {sum(sleeps)/len(sleeps):.1f}\n"
    return text


def build_chart(db, user_id):
    rows = db.get_entries(user_id, 30)

    if len(rows) < 2:
        return None

    df = pd.DataFrame(rows, columns=['date', 'mood', 'work', 'sleep', 'comment'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['mood'], marker='o', color='#8e44ad', linewidth=2, label='Настроение')
    plt.fill_between(df['date'], df['mood'], alpha=0.2, color='#8e44ad')

    plt.title('Динамика настроения (30 дней)', fontsize=14)
    plt.ylabel('Оценка (1-5)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.ylim(0, 6)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()

    return buf