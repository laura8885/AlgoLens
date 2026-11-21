from pathlib import Path
import json
import sys
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed' / 'algorithm_samples.csv'
MODELS = ROOT / 'models'
RESULTS = ROOT / 'results'


def main():
    df = pd.read_csv(DATA)
    rng = np.random.default_rng(42)
    test_groups = []
    for label in sorted(df['label'].unique()):
        label_groups = sorted(df.loc[df['label'] == label, 'template_group'].unique())
        test_groups.extend(rng.choice(label_groups, size=2, replace=False).tolist())
    test_mask = df['template_group'].isin(test_groups)
    train, test = df.loc[~test_mask], df.loc[test_mask]
    x_train, x_test = train['code'], test['code']
    y_train, y_test = train['label'], test['label']

    features = FeatureUnion([
        ('word', TfidfVectorizer(analyzer='word', token_pattern=r'(?u)\b\w+\b', ngram_range=(1, 2), sublinear_tf=True)),
        ('char', TfidfVectorizer(analyzer='char', ngram_range=(3, 5), min_df=1, sublinear_tf=True)),
    ])
    models = {
        'tfidf_logistic_regression': Pipeline([('features', features), ('classifier', LogisticRegression(max_iter=3000, class_weight='balanced'))]),
        'tfidf_linear_svm': Pipeline([('features', features), ('classifier', LinearSVC(class_weight='balanced'))]),
    }
    summary = {
        'dataset': {
            'total_examples': int(len(df)),
            'train_examples': int(len(train)),
            'test_examples': int(len(test)),
            'classes': sorted(df['label'].unique().tolist()),
            'split_method': 'Stratified grouped holdout: two complete original template families per class are held out, keeping all variants of a template together',
            'data_note': 'All current examples are original controlled examples created for this project; they are not external real-world repository samples.',
        },
        'models': {},
    }
    best_name, best_score, best_model = None, -1, None
    for name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        score = accuracy_score(y_test, pred)
        report = classification_report(y_test, pred, output_dict=True, zero_division=0)
        summary['models'][name] = {
            'accuracy': float(score),
            'macro_f1': float(report['macro avg']['f1-score']),
            'weighted_f1': float(report['weighted avg']['f1-score']),
            'classification_report': report,
        }
        if score > best_score:
            best_name, best_score, best_model = name, score, model
    MODELS.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    joblib.dump(best_model, MODELS / 'classifier.joblib')
    summary['selected_model'] = best_name
    summary['selected_model_reason'] = 'Highest held-out accuracy among the implemented baselines; this is a small controlled dataset and results should not be interpreted as real-world performance.'
    summary['selected_model_classification_report'] = summary['models'][best_name]['classification_report']
    y_pred = best_model.predict(x_test)
    labels = sorted(df['label'].unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(9, 7))
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, xticks_rotation=35, colorbar=False)
    ax.set_title('AlgoLens held-out test confusion matrix')
    fig.tight_layout()
    fig.savefig(RESULTS / 'confusion_matrix.png', dpi=160)
    plt.close(fig)
    summary['test_examples_by_class'] = test['label'].value_counts().sort_index().to_dict()
    (RESULTS / 'metrics.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps({'selected_model': best_name, 'accuracy': best_score, 'macro_f1': summary['models'][best_name]['macro_f1'], 'dataset': summary['dataset']}, indent=2))

if __name__ == '__main__':
    main()
