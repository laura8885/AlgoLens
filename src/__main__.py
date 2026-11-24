import json

from src.recognition import train

if __name__ == "__main__":
    print(json.dumps(train(), indent=2))
