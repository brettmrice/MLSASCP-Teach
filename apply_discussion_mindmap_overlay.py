import os
import re
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

OVERLAY_ASSET_FILES = [
    "discussion_mindmap.css",
    "discussion_quiz.css",
    "discussion_mindmap.js",
    "discussion_quiz.js"
]

def get_overlay_asset_version(shared_dir=None):
    if not shared_dir or not os.path.exists(shared_dir):
        return "20261019"
    mtimes = []
    for f in OVERLAY_ASSET_FILES:
        p = os.path.join(shared_dir, f)
        if os.path.isfile(p):
            try:
                mtimes.append(os.path.getmtime(p))
            except OSError:
                pass
    if mtimes:
        return datetime.fromtimestamp(max(mtimes), timezone.utc).strftime("%Y%m%d")
    return "20261019"

def update_discussion_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    file_dir = os.path.dirname(file_path)
    shared_dir = os.path.join(ROOT_DIR, "shared")
    rel_to_shared = os.path.relpath(shared_dir, file_dir).replace("\\", "/")
    version = get_overlay_asset_version(shared_dir)

    css_mindmap = f'    <!-- Portable Discussion Mind Map Overlay -->\n    <link rel="stylesheet" href="{rel_to_shared}/discussion_mindmap.css?v={version}">'
    css_quiz = f'    <!-- Portable Discussion Quiz Overlay -->\n    <link rel="stylesheet" href="{rel_to_shared}/discussion_quiz.css?v={version}">'

    # Clean old links
    content = re.sub(r'<link\s+rel="stylesheet"\s+href="[^"]*discussion_mindmap\.css(?:\?[^"]*)?">', f'<link rel="stylesheet" href="{rel_to_shared}/discussion_mindmap.css?v={version}">', content)
    content = re.sub(r'<link\s+rel="stylesheet"\s+href="[^"]*discussion_quiz\.css(?:\?[^"]*)?">', f'<link rel="stylesheet" href="{rel_to_shared}/discussion_quiz.css?v={version}">', content)

    # Clean scripts
    content = re.sub(r'<script\s+src="[^"]*mindmaps_manifest\.js(?:\?[^"]*)?"></script>\s*', '', content)
    content = re.sub(r'<script\s+src="[^"]*discussions_manifest\.js(?:\?[^"]*)?"></script>\s*', '', content)
    content = re.sub(r'<script\s+src="[^"]*discussion_mindmap\.js(?:\?[^"]*)?"></script>\s*', '', content)
    content = re.sub(r'<script\s+src="[^"]*discussion_quiz\.js(?:\?[^"]*)?"></script>\s*', '', content)

    # Ensure CSS exists
    if 'discussion_mindmap.css' not in content:
        if 'github-markdown.min.css">' in content:
            content = content.replace(
                'github-markdown.min.css">\n',
                'github-markdown.min.css">\n' + css_mindmap + '\n'
            )
        elif '</head>' in content:
            content = content.replace('</head>', css_mindmap + '\n</head>')

    if 'discussion_quiz.css' not in content:
        if 'discussion_mindmap.css' in content:
            content = re.sub(
                r'(<link\s+rel="stylesheet"\s+href="[^"]*discussion_mindmap\.css[^"]*">)',
                r'\1\n' + css_quiz,
                content
            )
        elif '</head>' in content:
            content = content.replace('</head>', css_quiz + '\n</head>')

    # Ensure JS scripts exist
    js_stack = (
        f'    <!-- Portable Discussion Mind Map & Navigation Overlay Engine & Data -->\n'
        f'    <script src="{rel_to_shared}/mindmaps_manifest.js?v={version}"></script>\n'
        f'    <script src="{rel_to_shared}/discussions_manifest.js?v={version}"></script>\n'
        f'    <script src="{rel_to_shared}/discussion_mindmap.js?v={version}"></script>\n'
        f'    <script src="{rel_to_shared}/discussion_quiz.js?v={version}"></script>'
    )

    if '</body>' in content:
        content = content.replace('</body>', js_stack + '\n</body>')

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    count = 0
    updated = 0
    for folder in ['Hematology', 'Body_Fluids']:
        folder_path = os.path.join(ROOT_DIR, folder)
        if not os.path.exists(folder_path):
            continue
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith('_Discussion.html') or file.endswith('_Complete_Discussion.html'):
                    count += 1
                    file_path = os.path.join(root, file)
                    if update_discussion_file(file_path):
                        print(f"Updated: {os.path.relpath(file_path, ROOT_DIR)}")
                        updated += 1
                    else:
                        print(f"Verified: {os.path.relpath(file_path, ROOT_DIR)}")

    print(f"\nDone! Processed {count} discussions ({updated} updated).")

if __name__ == '__main__':
    main()
