# AlgoLens

**An ML-assisted algorithm recognition and interactive visualization prototype.**

AlgoLens accepts a Python code snippet, predicts which of six classical algorithms it most resembles, displays typical complexity information, and provides step-by-step visual traces for the algorithms.

## Current capabilities

- Six labels: binary search, linear search, bubble sort, insertion sort, quick sort, and merge sort.
- Two machine-learning baselines: TF-IDF + Logistic Regression and TF-IDF + Linear SVM.
- Grouped train/test split by original template family to reduce near-duplicate leakage.
- Accuracy, macro F1, weighted F1, per-class metrics, and confusion matrix.
- Streamlit interface for code recognition, algorithm traces, and model evaluation.

## Important dataset limitation

The dataset currently included in `data/processed/algorithm_samples.csv` contains **240 original controlled examples** created specifically for this project (40 per class). The examples are programmatically varied versions of eight hand-written templates per class. They are not scraped from GitHub, and they are not a representative real-world code corpus. The held-out test results therefore measure recognition among related controlled implementations, not generalization to arbitrary code found online.

This is an honest baseline and a reproducible starting point. The next research step is to add independently sourced implementations with verified labels, source URLs, licenses, and repository-level splits. See `DATASET.md` before extending the corpus.

## Run locally

1. Open this folder in VS Code.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Regenerate the dataset and train the models:

   ```bash
   python src/generate_dataset.py
   python src/train_model.py
   ```

5. Launch the app:

   ```bash
   streamlit run app.py
   ```

Streamlit will print a local address, usually `http://localhost:8501`. Keep the terminal running while using the app. To stop it, press `Control + C` in the terminal.

## Project structure

```text
AlgoLens/
├── app.py
├── data/processed/algorithm_samples.csv
├── models/classifier.joblib
├── results/metrics.json
├── results/confusion_matrix.png
├── src/generate_dataset.py
├── src/train_model.py
├── src/predict.py
├── src/visualizations.py
├── tests/test_algorithms.py
├── DATASET.md
├── requirements.txt
└── README.md
```

## Reproducibility

The dataset generator and training script use fixed random seeds. The model artifact is generated locally by `src/train_model.py`; rerun training after changing the dataset. Metrics are saved in `results/metrics.json`.

## Limitations and next steps

- The current dataset is small and controlled; a model can learn template-specific patterns.
- Raw SVM decision scores shown by the interface are not calibrated probabilities.
- The app does not execute submitted code. It only classifies source text and separately visualizes the selected algorithm on sample numeric input.
- The six-class classifier does not support arbitrary algorithms or guarantee correct identification.
- A future version should add verified external examples, repository-level deduplication, a stronger code representation such as CodeBERT, robustness tests, and broader evaluation.

## License and attribution

The project code is provided under the MIT License in `LICENSE`. The initial dataset consists of original examples written for AlgoLens. No third-party source code is redistributed in the current dataset.


## Interactive algorithm studio

The Explore algorithms workspace includes:

- Deliberately paced playback with play, pause, restart, previous/next controls, and three playback speeds.
- Step-by-step array states with labels for the active, compared, swapped, and pivot elements.
- Synchronized reference pseudocode highlighting and plain-language explanations for each operation. When a recognized submission has a clear matching source line, the app also highlights that line; otherwise it explains that the reference line is the conceptual equivalent.
- Recursion trees for Quick Sort and Merge Sort.
- A complexity explorer showing best, average, and worst-case growth notes and an illustrative input-size chart.
- Interactive prediction questions, pivot selection practice for Quick Sort, and feedback explaining incorrect answers.

The interface uses a restrained, editorial style: neutral surfaces, clear typography, and a small set of semantic colors for algorithm states. The interaction model takes inspiration from educational visualizers such as [VisuAlgo](https://visualgo.net/en/sorting), while the restrained palette and hierarchy follow general data-visualization guidance from [Tableau](https://help.tableau.com/current/blueprint/en-us/bp_visual_best_practices.htm) and [Carnegie Mellon University](https://www.cmu.edu/brand/brand-guidelines/data-viz.html).

The recursion tree and animation are educational representations of the selected algorithm. They are not a debugger or a guaranteed line-by-line execution trace of arbitrary submitted Python code.
