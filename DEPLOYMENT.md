# Deployment

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src
streamlit run app.py
```

The app opens at the local address printed by Streamlit (normally `http://localhost:8501`). Stop it with Ctrl+C in the terminal.

## Streamlit Community Cloud

1. Push the project folder to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository.
3. Select `app.py` as the entry point.
4. Deploy. The app can generate the model on first use if the model artifact is not present.

For reproducible deployment, run `python -m src` before committing so the dataset, metrics, and trained model are generated from the same code version.
