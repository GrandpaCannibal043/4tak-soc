from django import template
import re

register = template.Library()

@register.filter
def youtube_embed(url):
    if not url:
        return ""

    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    if not match:
        return ""

    video_id = match.group(1)

    return f"https://www.youtube.com/embed/{video_id}"
