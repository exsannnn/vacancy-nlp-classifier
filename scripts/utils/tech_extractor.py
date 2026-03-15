tech_keywords = {
    'python': ['python'],
    'javascript': ['javascript', 'js'],
    'java': ['java'],
    'c++': ['c++', 'с++'],
    'sql': ['sql', 'postgresql', 'mysql'],
    'docker': ['docker', 'контейнер'],
    'kubernetes': ['kubernetes', 'k8s'],
    'aws': ['aws', 'amazon'],
    'azure': ['azure'],
    'gcp': ['gcp', 'google cloud'],
    'pytorch': ['pytorch', 'torch'],
    'tensorflow': ['tensorflow', 'tf'],
    'scikit-learn': ['scikit-learn', 'sklearn'],
    'pandas': ['pandas'],
    'numpy': ['numpy'],
    'git': ['git'],
    'linux': ['linux'],
    'fastapi': ['fastapi'],
    'django': ['django'],
    'flask': ['flask']
}

def extract_tech_stack(text):
    text = str(text).lower()
    found = []
    for tech, keywords in tech_keywords.items():
        for kw in keywords:
            if kw in text:
                found.append(tech)
                break
    return ','.join(found)

def extract_tech_list(text):
    text = str(text).lower()
    found = []
    for tech, keywords in tech_keywords.items():
        for kw in keywords:
            if kw in text:
                found.append(tech)
                break
    return found