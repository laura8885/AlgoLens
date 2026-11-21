from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / 'models' / 'classifier.joblib'


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError('Trained model not found. Run: python src/generate_dataset.py && python src/train_model.py')
    return joblib.load(MODEL_PATH)


def predict_code(code, model=None):
    if not code or not code.strip():
        raise ValueError('Please paste a Python code snippet.')
    model = model or load_model()
    label = model.predict([code])[0]
    scores = None
    if hasattr(model, 'decision_function'):
        raw = model.decision_function([code])[0]
        classes = list(model.classes_)
        if len(classes) == 2:
            scores = {classes[1]: float(raw), classes[0]: float(-raw)}
        else:
            scores = {name: float(value) for name, value in zip(classes, raw)}
    return label, scores
