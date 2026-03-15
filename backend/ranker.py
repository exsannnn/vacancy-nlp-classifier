class RankerService:
    def __init__(self):
        pass

    def predict_quality(self, text):
        text = str(text).lower()
        score = 5

        good_indicators = {
            'зарплата': 2,
            'оклад': 2,
            'зп': 2,
            'удален': 1,
            'гибрид': 1,
            'официально': 1,
            'дмс': 1,
            'страхование': 1,
            'обучение': 1,
            'курсы': 0.5,
            'python': 0.5,
            'docker': 0.5,
            'sql': 0.5,
            'aws': 0.5,
            'ml': 0.5,
            'ai': 0.5,
            'pytorch': 0.5,
            'tensorflow': 0.5
        }

        for word, points in good_indicators.items():
            if word in text:
                score += points

        bad_indicators = ['сетевой маркетинг', 'млм', 'вклад под', 'обучение за счет', 'работа на дому без опыта']
        for word in bad_indicators:
            if word in text:
                score -= 3

        tech_count = 0
        tech_words = ['python', 'java', 'c++', 'javascript', 'sql', 'docker', 'kubernetes', 'aws', 'azure', 'gcp']
        for word in tech_words:
            if word in text:
                tech_count += 1

        score += min(tech_count * 0.3, 2)

        if 'senior' in text or 'lead' in text or 'руковод' in text:
            score += 1

        if 'junior' in text or 'начальный' in text or 'без опыта' in text:
            score -= 1

        if score > 10:
            score = 10
        if score < 1:
            score = 1

        return int(score)