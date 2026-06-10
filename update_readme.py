import json
import urllib.request
import re

def fetch_repos():
    url = "https://api.github.com/users/af-t/repos?per_page=100"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching repos: {e}")
        return []

def main():
    repos = fetch_repos()
    if not repos:
        print("No repos fetched, skipping update.")
        return

    # Filter out profile repo itself (af-t)
    filtered = [r for r in repos if r['name'].lower() != 'af-t']

    # Sort repos:
    # 1. stars (descending)
    # 2. updated/pushed time (descending)
    def sort_key(repo):
        stars = repo.get('stargazers_count', 0)
        pushed_at = repo.get('pushed_at', '')
        # We can compare pushed_at string directly for sorting
        return (stars, pushed_at)

    filtered.sort(key=sort_key, reverse=True)

    # Pick top 4 repositories
    top_repos = filtered[:4]

    # Generate the dynamic project cards
    cards = []
    # Display in a clean centered block, wrapping every 2 cards
    cards.append('<p align="center">')
    for i, repo in enumerate(top_repos):
        repo_name = repo['name']
        card_html = f'  <a href="https://github.com/af-t/{repo_name}">\n    <img src="https://my-readme-five.vercel.app/api/pin/?username=af-t&repo={repo_name}&theme=dracula" alt="{repo_name}" />\n  </a>'
        cards.append(card_html)
        # Add break or separate paragraphs to look neat
        if i == 1 and len(top_repos) > 2:
            cards.append('</p>\n<p align="center">')
    cards.append('</p>')

    projects_content = "\n".join(cards)

    # Read README.md
    readme_path = "README.md"
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading README.md: {e}")
        return

    # Replace block between <!-- PROJECTS_START --> and <!-- PROJECTS_END -->
    pattern = r"(<!-- PROJECTS_START -->).*?(<!-- PROJECTS_END -->)"
    replacement = f"\\1\n{projects_content}\n\\2"

    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count == 0:
        print("Placeholders not found in README.md!")
        return

    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated successfully with dynamic projects!")
    except Exception as e:
        print(f"Error writing README.md: {e}")

if __name__ == "__main__":
    main()
