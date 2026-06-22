import os
import importlib


def check_package(name):

    try:
        importlib.import_module(name)
        print(f"[OK] package: {name}")

    except Exception as e:
        raise Exception(f"Missing package: {name}") from e


def check_folder(path):

    if not os.path.exists(path):

        raise Exception(f"Missing folder: {path}")

    print(f"[OK] folder: {path}")


def main():

    packages = [
        "numpy",
        "pandas",
        "scipy",
        "sklearn",
        "openai",
        "aspose.cells"
    ]

    for pkg in packages:
        check_package(pkg)

    check_folder("../samples")
    check_folder("../output")

    print("\nEnvironment validation passed.")


if __name__ == "__main__":
    main()