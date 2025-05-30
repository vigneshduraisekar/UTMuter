import os
import re
from bs4 import BeautifulSoup
import glob
import webbrowser
import argparse

def extract_failure_details(elements, test_case_info, summary):
    """
    Extracts failure details from a list of HTML elements between test case headers.
    Skips header-only <font color="red"> blocks and only includes real failure details.
    """
    failure_details = []
    header_texts = {"Summary status", "Failed", "Checks failed"}
    for el in elements:
        for font in getattr(el, 'find_all', lambda *a, **k: [])('font', color=lambda c: c and c.lower() == 'red'):
            font_soup = BeautifulSoup(str(font), 'html.parser')
            td_texts = [td.get_text(strip=True) for td in font_soup.find_all('td')]
            # Skip if all <td> are headers or single value cells (headers or numbers)
            if td_texts and all(t in header_texts or t.isdigit() or not t for t in td_texts):
                continue
            # Only append if it contains an <h4> (real failure details) or multiple lines
            if font_soup.find('h4') or len(font_soup.get_text(strip=True).splitlines()) > 1:
                failure_html = str(font)
                failure_details.append({
                    "test_case": test_case_info,
                    "summary": summary,
                    "failure": {"Details": failure_html}
                })
    return failure_details

def consolidate_mutation_reports(report_files, func_name):
    """
    Consolidates Cantata mutation test reports to generate a summary report for a specific function.
    Finds total number of test cases by counting <H4> tags with the function name in the test case header.
    """
    mutation_summary = {}
    mutation_scores = []
    total_test_cases = 0  # We'll count these using <H4> tags

    # Count total test cases for this function across all files
    test_case_pattern = re.compile(rf'Test Case:\s*\d+:\s*{re.escape(func_name)}\b')
    test_case_set = set()
    for report_file in report_files:
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                for h4 in soup.find_all('h4'):
                    h4_text = h4.get_text(strip=True)
                    if test_case_pattern.search(h4_text):
                        test_case_set.add(h4_text)
        except Exception as e:
            print(f"Error processing report file {report_file}: {e}")
            continue
    total_test_cases = len(test_case_set)

    # Now process each mutation file for killed tests and failure details
    for report_file in report_files:
        mutation_type = os.path.splitext(os.path.basename(report_file))[0].replace("mut_", "")
        killed_tests = 0
        failure_details = []

        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')

                # Parse each test case block
                for h4 in soup.find_all('h4'):
                    h4_text = h4.get_text(strip=True)
                    # Only process test cases for the current function
                    if h4_text.startswith("Test Case:") and f": {func_name}" in h4_text:
                        test_case_info = h4_text
                        # Find the next table (summary)
                        summary_table = h4.find_next('table')
                        summary = {}
                        failed = False
                        if summary_table:
                            for row in summary_table.find_all('tr'):
                                cols = row.find_all('td')
                                if len(cols) == 2:
                                    key = cols[0].get_text(strip=True)
                                    value = cols[1].get_text(strip=True)
                                    summary[key] = value
                                    if key.lower() == "summary status" and value.lower() == "failed":
                                        failed = True
                                        killed_tests += 1
                        # Only collect failure details if failed
                        if failed:
                            next_h4 = h4.find_next(lambda tag: tag.name == 'h4' and tag.text.strip().startswith("Test Case:"))
                            elements = []
                            elem = h4.next_sibling
                            while elem and elem != next_h4:
                                if getattr(elem, 'name', None):
                                    elements.append(elem)
                                elem = elem.next_sibling
                            failure_details.extend(extract_failure_details(elements, test_case_info, summary))

        except FileNotFoundError:
            print(f"Error: Report file not found: {report_file}")
            continue
        except Exception as e:
            print(f"Error processing report file {report_file}: {e}")
            continue

        # No need for mutation_score or survived/killed columns, just status
        mutation_summary[mutation_type] = {
            "killed_tests": killed_tests,
            "failure_details": failure_details
        }

    # Calculate average mutation score across all mutation types (if needed for summary)
    if mutation_summary:
        mutation_score = round(
            sum(1 if m["killed_tests"] > 0 else 0 for m in mutation_summary.values()) / len(mutation_summary) * 100, 2
        )
    else:
        mutation_score = 0

    report = {
        "mutation_types": mutation_summary,
        "mutation_score": mutation_score,
        "total_test_cases": total_test_cases
    }

    return report

def consolidate_all_functions(report_files, report_folder):
    """Group report files by function name and consolidate each group."""
    function_reports = {}
    for file in report_files:
        rel_path = os.path.relpath(file, report_folder)
        parts = rel_path.split(os.sep)
        if len(parts) > 1:
            func_name = parts[0]
            function_reports.setdefault(func_name, []).append(file)
    consolidated = {}
    for func_name, files in function_reports.items():
        consolidated[func_name] = consolidate_mutation_reports(files, func_name)
    return consolidated

def render_failure_detail(detail):
    """Render a single failure detail as HTML."""
    html = [
        "<div style='margin-bottom:10px;padding-left:10px;border-left:2px solid #f00;'>",
        f"<b>Test Case:</b> {detail.get('test_case', '')}<br>",
        "<b>Summary:</b><ul>"
    ]
    for k, v in detail.get('summary', {}).items():
        html.append(f"<li>{k}: {v}</li>")
    html.append("</ul>")
    failure = detail.get('failure', {})
    if failure:
        html.append("<b>Failure:</b>")
        # If the failure dict has a 'Details' key, render its value as raw HTML
        if "Details" in failure:
            html.append(f"<div>{failure['Details']}</div>")
        else:
            html.append("<ul>")
            for k, v in failure.items():
                html.append(f"<li>{k}: {v}</li>")
            html.append("</ul>")
    html.append("</div>")
    return ''.join(html)

def render_mutation_type_row(mutation_type, data, func_name=None):
    """Render a mutation type row and its failure details section."""
    unique_id = f"{func_name}_{mutation_type}" if func_name else mutation_type
    killed_mutants = data.get('killed_tests', 0)
    total_cases = data.get('total_test_cases', 0)
    # If any killed_mutants > 0, mark as failed, else survived
    if killed_mutants > 0:
        status = "<span style='color:green;font-weight:bold;'>Killed</span>"
    else:
        status = "<span style='color:red;font-weight:bold;'>Survived</span>"

    row = [
        f"<tr>",
        f"<td class='clickable' onclick=\"toggleFailureDetails('{unique_id}-details')\">{mutation_type}</td>",
        f"<td>{status}</td>",
        f"</tr>",
        f"<tr>",
        f"<td colspan='2'>",
        f"<div id='{unique_id}-details' class='failure-details'>",
        "<b>Failure Details:</b><br>"
    ]
    if data['failure_details']:
        for detail in data['failure_details']:
            row.append(render_failure_detail(detail))
    else:
        row.append("<p>No failure details found.</p>")
    row.append("</div></td></tr>")
    return ''.join(row)

def generate_html_report(consolidated_reports, output_file="mutation_test_summary_report.html"):
    """Generate a single HTML report with a section for each function."""
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<title>Mutation Test Summary Report</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; background-color: #f0f0f0; }",
        "table { border-collapse: collapse; width: 100%; background-color: white; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background-color: #4CAF50; color: white; }",
        "tr:nth-child(even) {background-color: #f2f2f2;}",
        ".summary { font-weight: bold; color: #333; }",
        ".failure-details { display: none; padding: 10px; border: 1px solid #ccc; margin-top: 5px; }",
        ".clickable { cursor: pointer; color: #007bff; text-decoration: underline; }",
        "h1 { color: #333; }",
        ".sim-hackers-watermark {",
        "  position: fixed;",
        "  top: 20px;",
        "  right: 40px;",
        "  font-size: 3em;",
        "  color: rgba(128,128,128,0.5);",
        "  font-weight: bold;",
        "  z-index: 9999;",
        "  pointer-events: none;",
        "}",
        "</style>",
        "<script>",
        "function toggleFailureDetails(id) {",
        "    var details = document.getElementById(id);",
        "    if (details.style.display === 'none') {",
        "        details.style.display = 'block';",
        "    } else {",
        "        details.style.display = 'none';",
        "    }",
        "}",
        "</script>",
        "</head>",
        "<body>",
        "<div class='sim-hackers-watermark'>Sim_Hackers</div>",
        "<h1>Mutation Test Summary Report</h1>",
    ]

    # --- Add summary table for all functions at the beginning ---
    html_parts.append("<h2 style='color:#333;'>Function Summary</h2>")
    html_parts.append("""
    <table style="table-layout: auto; width: auto; min-width: 0; margin-bottom: 30px;">
        <thead>
            <tr>
                <th style="width: 250px; white-space:nowrap;">Function Name</th>
                <th style="width: 180px; white-space:nowrap;">Number of Mutations</th>
                <th style="width: 200px; white-space:nowrap;">Mutation Score (%)</th>
            </tr>
        </thead>
        <tbody>
    """)
    for func_name, report in consolidated_reports.items():
        num_mutations = len(report["mutation_types"])
        mutation_score = report["mutation_score"]
        html_parts.append(f"<tr><td style='white-space:nowrap'>{func_name}</td><td>{num_mutations}</td><td><span style='font-size:1.2em;font-weight:bold'>{mutation_score:.2f}</span></td></tr>")
    html_parts.append("</tbody></table>")
    # ------------------------------------------------------------

    # Now add individual mutation summaries
    html_parts.append("<h2 style='color:#333;'>Detailed Summary</h2>")
    for func_name, report in consolidated_reports.items():
        html_parts.append(f"<h3 style='color:#555;'>{func_name}</h3>")
        html_parts.append("""
        <table>
        <thead>
        <tr>
            <th>Mutation Type</th>
            <th>Killed/Survived</th>
        </tr>
        </thead>
        <tbody>
        """)
        for mutation_type, data in report["mutation_types"].items():
            data['total_test_cases'] = report.get('total_test_cases', 0)
            html_parts.append(render_mutation_type_row(mutation_type, data, func_name=func_name))
        html_parts.append("</tbody></table>")

    html_parts.extend([
        "<button onclick=\"window.print()\">Save as PDF</button>",
        "</body>",
        "</html>"
    ])

    html_content = '\n'.join(html_parts)
    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"HTML report generated: {output_file}")
    return output_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Consolidate mutation test reports and generate an HTML summary.")
    parser.add_argument("report_folder", help="Path to the folder containing the mutation test reports.")
    args = parser.parse_args()

    report_folder = args.report_folder

    if not os.path.isdir(report_folder):
        print("Error: Invalid report folder path.")
    else:
        # Recursively find all mut_*.html files in all subfolders
        report_files = glob.glob(os.path.join(report_folder, "**", "mut_*.html"), recursive=True)
        if not report_files:
            print("Error: No report files found in the specified folder.  Please ensure the folder contains the correct HTML reports.")
        else:
            consolidated_reports = consolidate_all_functions(report_files, report_folder)
            html_report_file = generate_html_report(consolidated_reports)
            webbrowser.open('file://' + os.path.abspath(html_report_file))