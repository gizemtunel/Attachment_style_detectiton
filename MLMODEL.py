import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("C:/Users/HUAWEI/Desktop/birlesik_sarkilar.csv")

df.dropna(subset=['lyrics', 'mood'], inplace=True)

X = df['lyrics']
y = df['mood']

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

models = {
    "Lojistik Regresyon": LogisticRegression(max_iter=1000),
    "Destek Vektör Makinesi (SVM)": LinearSVC(),
    "Rastgele Orman": RandomForestClassifier(),
}

for name, model in models.items():
    model.fit(X_train_vec, y_train)
    predictions = model.predict(X_test_vec)
    acc = accuracy_score(y_test, predictions)
    print(f"\n=== {name} ===")
    print("Doğruluk:", round(acc * 100, 2), "%")
    print(classification_report(y_test, predictions, target_names=label_encoder.classes_))
    

    cm = confusion_matrix(y_test, predictions)
    
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=label_encoder.classes_, 
                yticklabels=label_encoder.classes_)
    plt.title(f'{name} - Confusion Matrix')
    plt.xlabel('Tahmin Edilen')
    plt.ylabel('Gerçek')
    plt.show()
