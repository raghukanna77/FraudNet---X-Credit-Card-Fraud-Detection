"""
Quick setup verification script
Checks that all dependencies are properly installed
"""

import sys
import importlib


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False
    except Exception as e:
        print(f"⚠ {package_name} - INSTALLED (but import issue: {type(e).__name__})")
        return True  # Package is installed, just has import issues


def main():
    print("="*60)
    print("FraudNet-X Setup Verification")
    print("="*60)
    print("\nChecking dependencies...\n")
    
    packages = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("xgboost", "xgboost"),
        ("networkx", "networkx"),
        ("river", "river"),
        ("shap", "shap"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("streamlit", "streamlit"),
        ("plotly", "plotly"),
        ("imbalanced-learn", "imblearn"),
        ("loguru", "loguru"),
        ("pydantic", "pydantic"),
        ("joblib", "joblib"),
        ("pytest", "pytest"),
    ]
    
    # Separately check TensorFlow/Keras (known issues on Python 3.12)
    tf_packages = [
        ("tensorflow", "tensorflow"),
        ("keras", "keras"),
    ]
    
    results = []
    for pkg_name, import_name in packages:
        results.append(check_package(pkg_name, import_name))
    
    print("\nChecking deep learning packages (may show warnings)...")
    for pkg_name, import_name in tf_packages:
        results.append(check_package(pkg_name, import_name))
    
    print("\n" + "="*60)
    
    installed_count = sum(results)
    total_count = len(packages) + len(tf_packages)
    
    if installed_count >= len(packages):  # Core packages must be installed
        print(f"✅ {installed_count}/{total_count} dependencies installed!")
        print("\nNext steps:")
        print("1. Download the dataset from Kaggle")
        print("2. Place creditcard.csv in the data/ directory")
        print("3. Run: python train_pipeline.py --data data/creditcard.csv")
        print("4. Start API: uvicorn api.main:app --reload")
        print("5. Launch dashboard: streamlit run dashboard/app.py")
    else:
        print("❌ Some dependencies are missing")
        print("\nPlease run: pip install -r requirements.txt")
    
    print("="*60)


if __name__ == "__main__":
    main()
