from src.recognition import train

if __name__ == "__main__":
    metrics = train()
    for name, result in metrics["models"].items():
        print(f"{name}: accuracy={result['accuracy']:.3f}, macro_f1={result['macro_f1']:.3f}")
