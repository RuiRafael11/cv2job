import html


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def get_hex_color(pct):
    if pct >= 70:
        return "#34d399"
    if pct >= 40:
        return "#fbbf24"
    return "#f87171"


def gauge_svg(score, max_score=100):
    pct = min(score / max_score, 1.0)
    color = get_hex_color(pct * 100)
    r, cx, cy = 80, 100, 100
    circumference = 2 * 3.14159 * r
    dash = circumference * pct
    gap = circumference - dash
    return (
        f'<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="width:220px;height:220px;">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#27272a" stroke-width="12"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="12" '
        f'stroke-linecap="round" stroke-dasharray="{dash:.1f} {gap:.1f}" transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy - 5}" text-anchor="middle" font-family="Playfair Display,serif" '
        f'font-size="44" fill="#fafafa">{score}</text>'
        f'<text x="{cx}" y="{cy + 20}" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
        f'font-size="10" fill="#a1a1aa" letter-spacing="1">COM A VAGA</text>'
        f"</svg>"
    )


def subscore_circle(value, max_val, label):
    pct = value / max_val if max_val > 0 else 0
    color = get_hex_color(pct * 100)
    r = 28
    circ = 2 * 3.14159 * r
    dash = circ * pct
    gap = circ - dash
    return (
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:10px;'
        f'background:rgba(24,24,27,0.5);border-radius:12px;border:1px solid #27272a;">'
        f'<svg viewBox="0 0 70 70" style="width:60px;height:60px;">'
        f'<circle cx="35" cy="35" r="{r}" fill="none" stroke="#27272a" stroke-width="5"/>'
        f'<circle cx="35" cy="35" r="{r}" fill="none" stroke="{color}" stroke-width="5" '
        f'stroke-linecap="round" stroke-dasharray="{dash:.1f} {gap:.1f}" transform="rotate(-90 35 35)"/>'
        f'<text x="35" y="40" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
        f'font-size="14" font-weight="600" fill="#fafafa">{value}</text>'
        f"</svg>"
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.6rem;letter-spacing:1px;'
        f'text-transform:uppercase;color:#a1a1aa;text-align:center;">{label}</div>'
        f"</div>"
    )


def progress_bar_html(value, max_val, color=None):
    pct = min(value / max_val, 1.0) * 100 if max_val > 0 else 0
    c = color or get_hex_color(pct)
    return (
        f'<div class="progress-track">'
        f'<div class="progress-fill" style="width:{pct:.1f}%;background:{c};"></div>'
        f"</div>"
        f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.75rem;color:{c};'
        f'letter-spacing:1px;margin-top:8px;">{int(pct)}% DO CRITÉRIO</div>'
    )
