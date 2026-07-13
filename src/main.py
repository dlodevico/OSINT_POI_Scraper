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
    """Create a simple HTML page showing positive matches."""
    safe_username = html.escape(username)
    positive_matches = filter_positive_results(results)

    if not positive_matches:
        body = "<p>No matching accounts were found.</p>"
    else:
        rows = "".join(
            f"<li><a href=\"{url}\" target=\"_blank\">{name}</a></li>"
            for name, url, _ in positive_matches
        )
        body = f"<h2>Positive matches for {safe_username}</h2><ul>{rows}</ul>"

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>OSINT POI Scraper Results</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    input {{ padding: 0.5rem; width: 18rem; }}
    button {{ padding: 0.5rem 1rem; }}
    .card {{ border: 1px solid #ddd; padding: 1rem; border-radius: 8px; max-width: 36rem; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>OSINT POI Scraper</h1>
    <form action=\"/\" method=\"get\">
      <input name=\"username\" placeholder=\"Enter username\" value=\"{safe_username}\" />
      <button type=\"submit\">Search</button>
    </form>
    {body}
  </div>
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


def start_server(host: str = "127.0.0.1", port: int = 8000):
    server = ThreadingHTTPServer((host, port), SearchHandler)
    print(f"Serving UI at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        start_server()
    else:
        username = sys.argv[1] if len(sys.argv) > 1 else ""
        asyncio.run(main(username))