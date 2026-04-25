#!/usr/bin/env python3
"""
Gemini Image Generation Script
Calls Gemini image generation models through the 302.AI OpenAI-compatible chat relay.
Handles markdown response parsing and image download.
"""

import argparse
import base64
import json
import os
import re
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Create SSL context
try:
    import certifi
    _ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    _ssl_context = ssl._create_unverified_context()

def find_file_in_project(project_root: str, filename: str, source_dir: str = "") -> str | None:
    """Resolve an image path within the project with 3-layer fallback."""
    root = Path(project_root)

    exact = root / filename
    if exact.is_file():
        return str(exact)

    if source_dir:
        relative = Path(source_dir) / filename
        if relative.is_file():
            return str(relative)

    basename = Path(filename).name
    for match in root.rglob(basename):
        if match.is_file():
            return str(match)

    return None


def extract_images_from_markdown(content: str, project_root: str, source_dir: str, max_images: int = 14) -> list[dict]:
    """Extract and encode images from markdown content."""
    images = []
    supported_ext = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    mime_map = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.png': 'image/png', '.gif': 'image/gif', '.webp': 'image/webp'
    }

    # Pattern 1: Wikilink images ![[image.png]]
    wikilink_pattern = r'!\[\[([^\]]+)\]\]'
    for match in re.finditer(wikilink_pattern, content):
        if len(images) >= max_images:
            break
        img_ref = match.group(1).split('|')[0].strip()  # Remove alias
        ext = Path(img_ref).suffix.lower()
        if ext not in supported_ext:
            continue
        filepath = find_file_in_project(project_root, img_ref, source_dir)
        if filepath:
            try:
                with open(filepath, 'rb') as f:
                    data = base64.standard_b64encode(f.read()).decode('utf-8')
                images.append({
                    'mime_type': mime_map.get(ext, 'image/png'),
                    'data': data
                })
            except Exception as e:
                print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    # Pattern 2: Standard markdown images ![alt](url)
    md_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    for match in re.finditer(md_pattern, content):
        if len(images) >= max_images:
            break
        url = match.group(2).strip()

        # Check if it's a local file or URL
        if url.startswith(('http://', 'https://')):
            # Download remote image
            ext = Path(url.split('?')[0]).suffix.lower()
            if ext not in supported_ext:
                ext = '.png'
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=15, context=_ssl_context) as resp:
                    data = base64.standard_b64encode(resp.read()).decode('utf-8')
                    content_type = resp.headers.get('Content-Type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        mime = 'image/jpeg'
                    elif 'png' in content_type:
                        mime = 'image/png'
                    elif 'gif' in content_type:
                        mime = 'image/gif'
                    elif 'webp' in content_type:
                        mime = 'image/webp'
                    else:
                        mime = mime_map.get(ext, 'image/png')
                    images.append({'mime_type': mime, 'data': data})
            except Exception as e:
                print(f"Warning: Could not download {url}: {e}", file=sys.stderr)
        else:
            # Local file
            ext = Path(url).suffix.lower()
            if ext not in supported_ext:
                continue
            filepath = find_file_in_project(project_root, url, source_dir)
            if filepath:
                try:
                    with open(filepath, 'rb') as f:
                        data = base64.standard_b64encode(f.read()).decode('utf-8')
                    images.append({
                        'mime_type': mime_map.get(ext, 'image/png'),
                        'data': data
                    })
                except Exception as e:
                    print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)

    return images


def strip_images_from_content(content: str) -> str:
    """Remove image embeds from markdown to get clean text content."""
    # Remove wikilink images
    content = re.sub(r'!\[\[([^\]]+)\]\]', '', content)
    # Remove markdown images
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', '', content)
    # Clean up excess blank lines
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def extract_image_url_from_markdown(markdown_text: str) -> str | None:
    """Extract image URL from markdown response like ![](https://...)"""
    # Look for ![...](url) pattern
    pattern = r'!\[[^\]]*\]\(([^)]+)\)'
    match = re.search(pattern, markdown_text)
    if match:
        return match.group(1)
    
    # Also try to find bare URLs starting with http
    url_pattern = r'(https?://[^\s\)]+)'
    match = re.search(url_pattern, markdown_text)
    if match:
        return match.group(1)
    
    return None


def download_image_as_base64(url: str) -> bytes | None:
    """Download image from URL and return as base64-encoded bytes."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30, context=_ssl_context) as resp:
            img_bytes = resp.read()
            return base64.standard_b64encode(img_bytes)
    except Exception as e:
        print(f"Error downloading image from {url}: {e}", file=sys.stderr)
        return None


def call_gemini_image_api(
    api_key: str,
    model: str,
    system_prompt: str,
    text_content: str,
    images: list[dict]
) -> str | None:
    """Call the Gemini image model through 302.AI and return markdown containing an image URL."""

    url = "https://api.302.ai/v1/chat/completions"

    # Build content parts - text first, then images
    content_parts = [
        {
            "type": "text",
            "text": text_content
        }
    ]
    
    for img in images:
        content_parts.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{img['mime_type']};base64,{img['data']}"
            }
        })

    # Build request in OpenAI chat format
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": content_parts
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 4096,
        "stream": False
    }

    data = json.dumps(body).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        },
        method='POST'
    )

    try:
        with urllib.request.urlopen(req, timeout=120, context=_ssl_context) as resp:
            result = json.loads(resp.read().decode('utf-8'))

        # Extract text response
        choices = result.get("choices", [])
        if not choices:
            print("Error: No choices in response", file=sys.stderr)
            print(f"Full response: {json.dumps(result, indent=2)}", file=sys.stderr)
            return None

        message = choices[0].get("message", {})
        
        # Handle both string and array content formats
        content = message.get("content")
        if isinstance(content, list):
            # Array format - extract text from parts
            text_response = ""
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text_response += part.get("text", "")
                elif isinstance(part, str):
                    text_response += part
            return text_response.strip() if text_response else None
        elif isinstance(content, str):
            # String format
            return content.strip()

        print("Error: Invalid content format in response", file=sys.stderr)
        print(f"Message: {json.dumps(message, indent=2)[:500]}", file=sys.stderr)
        return None

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Request Error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Generate image with Gemini image models via the 302.AI chat relay from markdown content")
    parser.add_argument("--api-key", help="302.AI relay API key")
    parser.add_argument("--model", default="gemini-3-pro-image-preview", help="Model name")
    parser.add_argument("--content-file", help="Path to markdown file (relative to project root or absolute)")
    parser.add_argument("--content-text", help="Direct text content (alternative to --content-file)")
    parser.add_argument("--system-prompt-file", help="Path to system prompt template file")
    parser.add_argument("--system-prompt-text", help="Direct system prompt text (alternative to file)")
    parser.add_argument("--dry-run", action="store_true", help="Print final prompts and exit without calling the API")
    parser.add_argument("--project-root", dest="project_root", default=".", help="Project root directory")
    parser.add_argument("--vault-root", dest="project_root", help=argparse.SUPPRESS)
    parser.add_argument("--include-images", action="store_true", help="Include images from markdown content")
    parser.add_argument("--max-images", type=int, default=14, help="Max images to include")
    parser.add_argument("--output-dir", help="Output directory for generated image")
    parser.add_argument("--task-dir")
    parser.add_argument("--output-name", help="Output filename (without extension)")

    args = parser.parse_args()
    project_root = os.path.abspath(args.project_root)
    api_key = args.api_key or os.getenv("AI_302AI_API_KEY")
    if not args.dry_run and not api_key:
        print("Error: Missing API key. Provide --api-key or set AI_302AI_API_KEY", file=sys.stderr)
        sys.exit(1)

    # Get content
    if args.content_file:
        content_path = os.path.join(project_root, args.content_file) if not os.path.isabs(args.content_file) else args.content_file
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        source_dir = os.path.dirname(content_path)
    elif args.content_text:
        if args.include_images:
            print("Error: --include-images requires --content-file", file=sys.stderr)
            sys.exit(1)
        content = args.content_text
        source_dir = project_root
    else:
        print("Error: Either --content-file or --content-text is required", file=sys.stderr)
        sys.exit(1)

    # Get system prompt
    if args.system_prompt_file:
        prompt_path = os.path.join(project_root, args.system_prompt_file) if not os.path.isabs(args.system_prompt_file) else args.system_prompt_file
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
    elif args.system_prompt_text:
        system_prompt = args.system_prompt_text
    else:
        print("Error: Provide --system-prompt-text or --system-prompt-file", file=sys.stderr)
        sys.exit(1)
    system_prompt = system_prompt.strip()
    if not system_prompt:
        print("Error: System prompt is empty", file=sys.stderr)
        sys.exit(1)

    # Extract images if requested
    images = []
    if args.include_images:
        images = extract_images_from_markdown(content, project_root, source_dir, args.max_images)
        print(f"Extracted {len(images)} images from markdown", file=sys.stderr)

    # Strip image syntax from text content sent to API
    text_content = strip_images_from_content(content)

    if args.dry_run:
        print("DRY_RUN_SYSTEM_PROMPT_BEGIN")
        print(system_prompt)
        print("DRY_RUN_SYSTEM_PROMPT_END")
        print("DRY_RUN_TEXT_CONTENT_BEGIN")
        print(text_content)
        print("DRY_RUN_TEXT_CONTENT_END")
        print(f"DRY_RUN_IMAGES:{len(images)}")
        return

    # Call API
    print(f"Calling Gemini image model via 302.AI relay ({args.model})...", file=sys.stderr)
    print(f"  Content length: {len(text_content)} chars, Images: {len(images)}", file=sys.stderr)

    markdown_response = call_gemini_image_api(
        api_key=api_key or "",
        model=args.model,
        system_prompt=system_prompt,
        text_content=text_content,
        images=images
    )

    if markdown_response is None:
        print("Error: Failed to get response from the Gemini image model via 302.AI relay", file=sys.stderr)
        sys.exit(1)

    # Extract image URL from markdown response
    print("Received relay response, parsing for image URL...", file=sys.stderr)
    image_url = extract_image_url_from_markdown(markdown_response)

    if not image_url:
        print(f"Error: No image URL found in response. Response: {markdown_response[:200]}", file=sys.stderr)
        sys.exit(1)

    print(f"Found image URL: {image_url}", file=sys.stderr)

    # Download image
    print(f"Downloading generated image...", file=sys.stderr)
    img_base64 = download_image_as_base64(image_url)

    if not img_base64:
        print("Error: Failed to download generated image", file=sys.stderr)
        sys.exit(1)

    img_bytes = base64.standard_b64decode(img_base64)

    # Save image
    output_dir = os.path.abspath(args.output_dir) if args.output_dir else os.path.join(project_root, "output")
    if args.task_dir:
        td = Path(args.task_dir)
        if td.is_absolute() or ".." in td.parts or "/" in args.task_dir or "\\" in args.task_dir:
            print("Error: --task-dir must be a simple folder name", file=sys.stderr)
            sys.exit(1)
        output_dir = os.path.join(output_dir, args.task_dir)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_name = args.output_name or f"generated_image_{timestamp}"
    output_filename = f"{output_name}.png"
    output_path = os.path.join(output_dir, output_filename)

    try:
        with open(output_path, 'wb') as f:
            f.write(img_bytes)
        print(f"Image saved: {output_path}", file=sys.stderr)

        rel_path = os.path.relpath(output_path, project_root)
        print(f"SUCCESS:{rel_path}")

    except Exception as e:
        print(f"Error saving image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
