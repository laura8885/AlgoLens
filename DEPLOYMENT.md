# GitHub and Streamlit deployment

## 1. Create the GitHub repository

1. Sign in to GitHub and open https://github.com/new.
2. Name the repository `AlgoLens`.
3. Choose Public if you want admissions reviewers to be able to view it.
4. Do not initialize it with a README, license, or .gitignore because these are already in this folder.
5. Create the repository.

## 2. Push this project

Open Terminal in this `AlgoLens` folder and run:

```bash
git init
git add .
git commit -m "Build AlgoLens algorithm recognition prototype"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/AlgoLens.git
git push -u origin main
```

Replace `YOUR-GITHUB-USERNAME` with your GitHub username. GitHub may ask you to authenticate in your browser.

## 3. Deploy the Streamlit app

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Choose **Create app**.
3. Select your `AlgoLens` repository and `main` branch.
4. Set the main file path to `app.py`.
5. Deploy.

The app uses the trained `models/classifier.joblib` artifact included in this project. If you retrain the model, commit and push the updated model and metrics so the hosted app uses the same version.

## Notes

- Install dependencies from `requirements.txt`.
- Do not put passwords, API keys, or private tokens in the repository.
- The initial model is small enough to load in the Streamlit app. Do not perform model training on every app launch.
