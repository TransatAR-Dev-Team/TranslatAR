import json
import os
import sys
from datetime import datetime

# HTML Template with added columns and better number formatting
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TranslatAR Coverage Dashboard</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; color: #334155; margin: 0; padding: 20px; }}
        .container {{ max-width: 1100px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }}

        header {{ background: #1e293b; color: white; padding: 20px 30px; }}
        h1 {{ margin: 0; font-size: 1.5rem; }}
        .timestamp {{ font-size: 0.875rem; color: #94a3b8; display: block; margin-top: 4px; }}

        .hero {{ padding: 30px; text-align: center; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }}
        .hero-title {{ font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 600; }}
        .hero-value {{ font-size: 3.5rem; font-weight: 800; margin: 10px 0; color: #1e293b; }}
        .hero-subtitle {{ font-size: 1rem; color: #64748b; }}

        table {{ w-width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 16px 20px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #f1f5f9; font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; }}

        /* Number columns alignment */
        .num-col {{ text-align: right; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}

        tr:hover {{ background: #f8fafc; }}

        .badge {{ padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.875rem; }}
        .bg-green {{ background: #dcfce7; color: #166534; }}
        .bg-yellow {{ background: #fef9c3; color: #854d0e; }}
        .bg-red {{ background: #fee2e2; color: #991b1b; }}

        .progress-bar {{ background: #e2e8f0; height: 8px; border-radius: 4px; overflow: hidden; width: 80px; display: inline-block; vertical-align: middle; margin-right: 10px; }}
        .progress-fill {{ height: 100%; transition: width 0.3s ease; }}

        a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>TranslatAR Code Coverage</h1>
            <span class="timestamp">Generated: {date}</span>
        </header>

        <div class="hero">
            <div class="hero-title">Total Project Coverage</div>
            <div class="hero-value" style="color: {total_color}">{total_pct}%</div>
            <div class="hero-subtitle">
                {total_covered} / {total_lines} lines covered across {service_count} services
            </div>
        </div>

        <table width="100%">
            <thead>
                <tr>
                    <th>Service</th>
                    <th>Type</th>
                    <th class="num-col">Total Lines</th>
                    <th class="num-col">Covered</th>
                    <th>Coverage</th>
                    <th>Report</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </div>
</body>
</html>
"""


def get_color_hex(percentage):
    if percentage >= 80:
        return "#166534"  # Green
    if percentage >= 50:
        return "#854d0e"  # Yellow
    return "#991b1b"  # Red


def get_badge_class(percentage):
    if percentage >= 80:
        return "bg-green"
    if percentage >= 50:
        return "bg-yellow"
    return "bg-red"


def parse_python_coverage(json_path):
    """Returns (total_statements, covered_statements, percentage)"""
    try:
        with open(json_path) as f:
            data = json.load(f)
            totals = data.get("totals", {})
            total = totals.get("num_statements", 0)
            covered = totals.get("covered_lines", 0)
            pct = totals.get("percent_covered", 0)
            return total, covered, round(pct, 2)
    except Exception as e:
        print(f"Error parsing {json_path}: {e}")
        return 0, 0, 0


def parse_js_coverage(json_path):
    """Returns (total_lines, covered_lines, percentage)"""
    try:
        with open(json_path) as f:
            data = json.load(f)
            lines = data.get("total", {}).get("lines", {})
            total = lines.get("total", 0)
            covered = lines.get("covered", 0)
            pct = lines.get("pct", 0)
            return total, covered, round(pct, 2)
    except Exception as e:
        print(f"Error parsing {json_path}: {e}")
        return 0, 0, 0


def main():
    root_dir = sys.argv[1]
    rows = ""

    # Aggregators
    grand_total_lines = 0
    grand_covered_lines = 0
    services_found = 0

    services = sorted(
        [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
    )

    for service in services:
        service_path = os.path.join(root_dir, service)
        total = 0
        covered = 0
        pct = 0
        lang_type = "Unknown"

        # Detect Python report
        if os.path.exists(os.path.join(service_path, "coverage.json")):
            total, covered, pct = parse_python_coverage(
                os.path.join(service_path, "coverage.json")
            )
            lang_type = "Python"
        # Detect JS report
        elif os.path.exists(os.path.join(service_path, "coverage-summary.json")):
            total, covered, pct = parse_js_coverage(
                os.path.join(service_path, "coverage-summary.json")
            )
            lang_type = "TypeScript"
        else:
            continue

        services_found += 1
        grand_total_lines += total
        grand_covered_lines += covered

        badge_class = get_badge_class(pct)
        color_hex = get_color_hex(pct)
        link = f"{service}/index.html"

        pretty_name = service.replace("-", " ").replace("_", " ").title()

        # Build the HTML row
        rows += f"""
        <tr>
            <td>
                <div style="font-weight: 600;">{pretty_name}</div>
            </td>
            <td>{lang_type}</td>
            <td class="num-col">{total:,}</td>
            <td class="num-col">{covered:,}</td>
            <td>
                <div class="progress-bar"><div class="progress-fill" style="width: {pct}%; background: {color_hex};"></div></div>
                <span class="badge {badge_class}">{pct}%</span>
            </td>
            <td><a href="{link}">View Details &rarr;</a></td>
        </tr>
        """

    # Calculate Grand Total Percentage
    grand_pct = 0
    if grand_total_lines > 0:
        grand_pct = round((grand_covered_lines / grand_total_lines) * 100, 2)

    total_color = get_color_hex(grand_pct)

    html = HTML_TEMPLATE.format(
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        rows=rows,
        total_pct=grand_pct,
        total_covered=f"{grand_covered_lines:,}",
        total_lines=f"{grand_total_lines:,}",
        service_count=services_found,
        total_color=total_color,
    )

    # --- FIX: Ensure the path is clean/absolute before printing ---
    output_path = os.path.join(root_dir, "index.html")
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard generated at {os.path.abspath(output_path)}")
    print(
        f"Total Coverage: {grand_pct}% ({grand_covered_lines}/{grand_total_lines} lines)"
    )


if __name__ == "__main__":
    main()
