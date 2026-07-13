import asyncio
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import aiohttp

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Instagram": "https://www.instagram.com/{}/",
    "Twitter/X": "https://twitter.com/{}",
    "Archive.org": "https://archive.org/details/@{}",
}


def filter_positive_results(results):
    """Return only results marked as active."""
    return [result for result in results if result[2] == "Active"]


async def check_platform(session, name, username, url_template):
    """Checks if a username exists on a specific platform."""
    url = url_template.format(username)
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                return (name, url, "Active")
            if response.status == 404:
                return (name, url, "Not Found")
            return (name, url, f"Error: {response.status}")
    except Exception as exc:
        return (name, url, f"Failed: {exc}")


async def run_scraper(target_username):
    """Run the asynchronous checks and return the results."""
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = [
            check_platform(session, name, target_username, url_template)
            for name, url_template in PLATFORMS.items()
        ]
        return await asyncio.gather(*tasks)


def build_results_html(username, results):
    """Create a polished HTML page showing positive matches."""
    safe_username = html.escape(username)
    positive_matches = filter_positive_results(results)

    if not results:
        table_rows = "<tr><td colspan='3'>Enter a username to begin.</td></tr>"
    else:
        table_rows = "".join(
            f"<tr><td>{html.escape(name)}</td><td><span class='badge {status.lower().replace(' ', '-')}'>{html.escape(status)}</span></td><td><a href=\"{html.escape(url)}\" target=\"_blank\">Open</a></td></tr>"
            for name, url, status in results
        )

    summary_text = (
        f"<p class='summary'>Showing {len(positive_matches)} positive match(es) for <strong>{safe_username}</strong>.</p>"
        if username
        else "<p class='summary'>Search for a username to review potential social accounts.</p>"
    )

    toggle_checked = "checked" if username else ""

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>OSINT POI Scraper Results</title>
  <style>
    body {{
      font-family: 'Segoe UI', Arial, sans-serif;
      margin: 0;
      padding: 2rem;
      background: linear-gradient(135deg, #0f172a, #1e3a8a);
      color: #e2e8f0;
    }}
    .card {{
      max-width: 860px;
      margin: 0 auto;
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 2rem;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.25);
    }}
    h1 {{ margin-top: 0; }}
    form {{ display: flex; gap: 0.75rem; margin-bottom: 1rem; align-items: center; }}
    input {{
      flex: 1;
      padding: 0.7rem 0.9rem;
      border-radius: 8px;
      border: 1px solid #64748b;
      background: #111827;
      color: #f8fafc;
    }}
    button {{
      padding: 0.7rem 1rem;
      border: none;
      border-radius: 8px;
      background: #38bdf8;
      color: #082f49;
      cursor: pointer;
      font-weight: 600;
    }}
    .toggle-row {{ display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; color: #cbd5e1; }}
    .summary {{ color: #cbd5e1; margin-bottom: 1rem; }}
    .version-banner {{
      display: inline-block;
      margin-bottom: 1rem;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      background: #f59e0b;
      color: #111827;
      font-size: 0.85rem;
      font-weight: 700;
      letter-spacing: 0.03em;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; }}
    th, td {{ padding: 0.75rem; border-bottom: 1px solid #334155; text-align: left; }}
    th {{ color: #7dd3fc; cursor: pointer; user-select: none; }}
    a {{ color: #7dd3fc; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .badge {{ display: inline-block; padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; }}
    .badge.active {{ background: #14532d; color: #dcfce7; }}
    .badge.not-found {{ background: #7f1d1d; color: #fee2e2; }}
    .badge.error, .badge.failed {{ background: #92400e; color: #fef3c7; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <div class=\"version-banner\">Version 2 - Updated UI</div>
    <h1>OSINT POI Scraper</h1>
    <p>Search for a username and review matching social accounts.</p>
    <form action=\"/\" method=\"get\">
      <input name=\"username\" placeholder=\"Enter username\" value=\"{safe_username}\" />
      <button type=\"submit\">Search</button>
    </form>
    <div class=\"toggle-row\">
      <input type=\"checkbox\" id=\"positive-only\" name=\"positive_only\" {toggle_checked} />
      <label for=\"positive-only\">Positive matches only</label>
    </div>
    {summary_text}
    <table id=\"results-table\">
      <thead>
        <tr>
          <th data-sort=\"platform\">Platform</th>
          <th data-sort=\"status\">Status</th>
          <th data-sort=\"link\">Link</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>
  <script>
    const table = document.getElementById('results-table');
    const headers = table.querySelectorAll('th');
    let sortDirection = 1;

    headers.forEach((header) => {{
      header.addEventListener('click', () => {{
        const sortKey = header.dataset.sort;
        const rows = Array.from(table.tBodies[0].rows);
        rows.sort((a, b) => {{
          const aText = a.cells[Array.from(headers).indexOf(header)].textContent.trim().toLowerCase();
          const bText = b.cells[Array.from(headers).indexOf(header)].textContent.trim().toLowerCase();
          return aText.localeCompare(bText) * sortDirection;
        }});
        rows.forEach((row) => table.tBodies[0].appendChild(row));
        sortDirection *= -1;
      }});
    }});
  </script>
</body>
</html>
"""


async def main(username: str = ""):
    if not username:
        print(build_results_html("", []))
        return

    results = await run_scraper(username)
    print(build_results_html(username, results))


class SearchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        username = query.get("username", [""])[0].strip()

        if username:
            results = asyncio.run(run_scraper(username))
        else:
            results = []

        html_content = build_results_html(username, results).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_content)))
        self.end_headers()
        self.wfile.write(html_content)

    def log_message(self, format, *args):
        return


def start_server(host: str = "0.0.0.0", port: int = 8000):
    server = ThreadingHTTPServer((host, port), SearchHandler)
    print(f"Serving UI at http://{host}:{port}")
    print("Accessible on your local network via your computer's IP address")
    server.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        start_server()
    else:
        username = sys.argv[1] if len(sys.argv) > 1 else ""
        asyncio.run(main(username))