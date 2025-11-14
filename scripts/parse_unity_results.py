import sys
import xml.etree.ElementTree as ET

def parse_and_summarize(xml_file_path):
    """
    Parses a Unity NUnit XML test results file, prints a summary,
    and returns an exit code.

    - Returns 0 if all tests passed.
    - Returns 1 if any test failed, was inconclusive, or the file is invalid.
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"\n❌ ERROR: Results file not found at '{xml_file_path}'. Unity may have crashed.", file=sys.stderr)
        print("\nMaybe there are compilation erorrs? Try opening the project in Unity Editor.\n", file=sys.stderr)
        return 1
    except ET.ParseError:
        print(f"\n❌ ERROR: Failed to parse XML file at '{xml_file_path}'. The file is likely empty or corrupt.", file=sys.stderr)
        return 1

    test_run = root.find("test-suite")
    if test_run is None:
        if root.tag == "test-run": # Fallback for certain error conditions
            test_run = root
        else:
            print(f"\n❌ ERROR: Could not find '<test-suite>' or '<test-run>' element in '{xml_file_path}'.", file=sys.stderr)
            return 1

    # Extract summary attributes
    total = int(test_run.get('total', 0))
    passed = int(test_run.get('passed', 0))
    failed = int(test_run.get('failed', 0))
    inconclusive = int(test_run.get('inconclusive', 0))
    skipped = int(test_run.get('skipped', 0))

    print(f"Total: {total}, Passed: {passed}, Failed: {failed}, Skipped: {skipped}, Inconclusive: {inconclusive}")

    if failed > 0 or inconclusive > 0:
        print("\n--- FAILED TESTS ---", file=sys.stderr)
        for test_case in root.findall(".//test-case"):
            if test_case.get('result') == 'Failed':
                name = test_case.get('fullname')

                failure_message_element = test_case.find(".//message")
                failure_message = failure_message_element.text.strip() if failure_message_element is not None and failure_message_element.text else "No message provided."

                stack_trace_element = test_case.find(".//stack-trace")
                stack_trace = stack_trace_element.text.strip() if stack_trace_element is not None and stack_trace_element.text else "No stack trace provided (check for compile errors)."

                print(f"\n❌ Test: {name}", file=sys.stderr)
                print(f"   Message: {failure_message}", file=sys.stderr)
                print(f"   Stack Trace:\n{stack_trace}\n", file=sys.stderr)
        return 1

    print("✅ All tests passed!")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse_unity_results.py <path_to_xml_file>", file=sys.stderr)
        sys.exit(1)

    results_file = sys.argv[1]
    exit_code = parse_and_summarize(results_file)
    sys.exit(exit_code)
