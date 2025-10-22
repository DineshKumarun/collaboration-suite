"""Run all tests"""
import sys
import subprocess

def run_test(test_file):
    """Run a test file and return result"""
    print(f"\n{'='*60}")
    print(f"Running {test_file}")
    print(f"{'='*60}\n")
    
    result = subprocess.run([sys.executable, test_file])
    return result.returncode == 0

if __name__ == "__main__":
    print("Running all tests...\n")
    
    tests = [
        "tests/test_video.py",
        "tests/test_audio.py",
        "tests/test_chat.py",
        "tests/test_file_transfer.py"
    ]
    
    results = {}
    for test in tests:
        try:
            results[test] = run_test(test)
        except Exception as e:
            print(f"Error running {test}: {e}")
            results[test] = False
    
    print(f"\n{'='*60}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*60}\n")
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{test}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    sys.exit(0 if passed == total else 1)
