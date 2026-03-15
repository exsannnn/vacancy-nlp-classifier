from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import config
import pickle
import os

with open(os.path.join(config.PROJECT_ROOT, 'data/processed/X_text.pkl'), 'rb') as f:
    X = pickle.load(f)

with open(os.path.join(config.PROJECT_ROOT, 'data/processed/y_category.pkl'), 'rb') as f:
    y_category = pickle.load(f)

with open(os.path.join(config.PROJECT_ROOT, 'data/processed/y_level.pkl'), 'rb') as f:
    y_level = pickle.load(f)

X_train, X_test, y_cat_train, y_cat_test = train_test_split(X, y_category, test_size=0.2, random_state=42)
_, _, y_lvl_train, y_lvl_test = train_test_split(X, y_level, test_size=0.2, random_state=42)

cat_model = LogisticRegression(max_iter=1000)
cat_model.fit(X_train, y_cat_train)

lvl_model = LogisticRegression(max_iter=1000)
lvl_model.fit(X_train, y_lvl_train)

cat_pred = cat_model.predict(X_test)
lvl_pred = lvl_model.predict(X_test)

cat_acc = accuracy_score(y_cat_test, cat_pred)
lvl_acc = accuracy_score(y_lvl_test, lvl_pred)

print(f'Точность категории: {cat_acc:.2f}')
print(f'Точность уровня: {lvl_acc:.2f}')

models_dir = os.path.join(config.PROJECT_ROOT, 'models', 'basic')
os.makedirs(models_dir, exist_ok=True)

with open(os.path.join(models_dir, 'cat_model.pkl'), 'wb') as f:
    pickle.dump(cat_model, f)

with open(os.path.join(models_dir, 'lvl_model.pkl'), 'wb') as f:
    pickle.dump(lvl_model, f)