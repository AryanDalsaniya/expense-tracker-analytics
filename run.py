import os
import sys
import subprocess

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # Detect virtualenv python executable
    if os.name == 'nt':
        venv_python = os.path.join(base_dir, '.venv', 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join(base_dir, '.venv', 'bin', 'python')

    python_executable = venv_python if os.path.exists(venv_python) else sys.executable

    print("\n" + "="*60)
    print("  Starting SpendWise Expense Tracker & Analytics...")
    print(f"  Python Runtime: {python_executable}")
    print("="*60 + "\n")

    app_path = os.path.join(base_dir, "app.py")
    try:
        subprocess.run([python_executable, app_path], check=True)
    except KeyboardInterrupt:
        print("\nSpendWise server stopped gracefully.")

if __name__ == "__main__":
    main()

