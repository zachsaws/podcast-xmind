#!/usr/bin/env python3
"""Maintainer-only artwork generator. Requires Pillow; runtime helpers do not."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BG, INK, MUTED, ACCENT, LINE = '#F4F0E6', '#183C35', '#55685C', '#B9472F', '#C5CCBE'


def font_path(explicit, bold=False):
    candidates = [explicit] if explicit else [
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf']
    for value in candidates:
        if value and Path(value).is_file():
            return value
    raise ValueError('Provide --font and --bold-font paths for this system')


def build(font, bold_font):
    assets = ROOT / 'assets'
    assets.mkdir(exist_ok=True)
    ledger = json.loads((ROOT / 'examples/synthetic/run/ledger.json').read_text())
    units = {u['id']: u for u in ledger['units']}
    assert units['U001']['disposition'] == 'included'
    assert '1000' in units['U001']['claim'] and '80' in units['U001']['claim']
    assert '0.80' in units['U004']['claim'] and '2' in units['U004']['claim']
    # All example copy below is editorial English rendering of the saved Chinese run.
    def font_at(size, bold=False):
        return ImageFont.truetype(bold_font if bold else font, size)
    def canvas():
        img = Image.new('RGB', (1280, 720), BG)
        return img, ImageDraw.Draw(img)
    def text(draw, xy, value, size=24, fill=INK, bold=False):
        draw.text(xy, value, font=font_at(size,bold), fill=fill)
    def line(draw, xy, fill=LINE, width=1):
        draw.line(xy, fill=fill, width=width)
    def base(draw, number, title):
        text(draw,(56,35),'PX / PODCAST XMIND',18,bold=True)
        text(draw,(926,35),'SYNTHETIC EXAMPLE',16,MUTED)
        line(draw,(56,80,1224,80),INK,2)
        text(draw,(56,104),number,17,ACCENT,bold=True)
        text(draw,(56,141),title,42,bold=True)
        line(draw,(56,652,1224,652))
        text(draw,(56,675),'Saved source + actual reading. Illustrated walkthrough, not an app recording.',18,MUTED)
    proof, d = canvas()
    base(d,'ONE CORRECTION. A DIFFERENT CONCLUSION.','Keep the detail that changes the story.')
    line(d,(630,226,630,610))
    text(d,(56,230),'THE HOST ASKS',17,MUTED,bold=True)
    text(d,(56,271),'1,000 paying',49,bold=True)
    text(d,(56,328),'customers?',49,bold=True)
    text(d,(56,407),'A question with a mistaken premise.',22,MUTED)
    text(d,(56,456),'Source: S0001 / 00:00',20,MUTED)
    text(d,(683,230),'THE GUEST CORRECTS',17,ACCENT,bold=True)
    text(d,(683,273),'1,000 registered',43,bold=True)
    text(d,(683,332),'80 paying',57,ACCENT,bold=True)
    text(d,(683,410),'As of end-June. Year unspecified.',22,MUTED)
    text(d,(683,452),'Sustainable growth is not yet proven.',22,MUTED)
    text(d,(683,516),'Reading U001 + U002 → S0002 / 00:20',20,bold=True)
    proof.save(assets/'evidence-tour.png',optimize=True)

    second, d = canvas()
    base(d,'THE NUMBER + ITS DENOMINATOR + ITS LIMIT.','A lower cost is only part of the story.')
    text(d,(56,240),'$2 → $0.80',78,ACCENT,bold=True)
    text(d,(56,340),'per completed task',34,bold=True)
    text(d,(56,397),'Not the price of a model call.',24,MUTED)
    text(d,(56,449),'Only with stable inputs.',24,bold=True)
    line(d,(675,230,675,602))
    text(d,(726,242),'THE COUNTEREXAMPLE',18,MUTED,bold=True)
    text(d,(726,295),'Hospital pilot',38,bold=True)
    text(d,(726,362),'Variable inputs → higher costs.',24,MUTED)
    text(d,(726,409),'The team paused the pilot.',24,MUTED)
    text(d,(726,493),'U004 + U006',23,ACCENT,bold=True)
    text(d,(726,535),'Read the mechanism and its boundary.',21,MUTED)

    third, d = canvas()
    base(d,'SCAN → DEEP READ → SOURCE EVIDENCE.','Choose how far you want to read.')
    columns=[(56,'01','SCAN','Answers + topic map'),(467,'02','DEEP READ','Reasoning + exceptions'),(878,'03','EVIDENCE','Original words + location')]
    for x,n,title,desc in columns:
        text(d,(x,247),n,66,ACCENT,bold=True)
        text(d,(x,347),title,26,bold=True)
        text(d,(x,399),desc,21,MUTED)
        line(d,(x,451,x+336,451))
    text(d,(56,509),'Partial input stays partial.',31,bold=True)
    text(d,(56,560),'A structural audit checks the ledger. Semantic review still checks the source.',22,MUTED)
    frames=[proof,second,third]
    palette_frames=[im.quantize(colors=96) for im in frames]
    palette_frames[0].save(assets/'evidence-tour.gif',save_all=True,append_images=palette_frames[1:],duration=[4200,4200,4200],loop=0,optimize=True,disposal=2)

    social=Image.new('RGB',(1280,640),BG);d=ImageDraw.Draw(social)
    text(d,(64,42),'PX / AGENT SKILL',19,bold=True)
    text(d,(944,42),'OPEN SOURCE · MIT',18,MUTED)
    line(d,(64,92,1216,92),INK,2)
    text(d,(58,124),'Podcast XMind',100,bold=True)
    text(d,(64,265),'Your podcast backlog,',46,bold=True)
    text(d,(64,323),'ready to read.',46,bold=True)
    text(d,(64,417),'Keep the corrections. Follow the reasoning. Trace the source.',25,MUTED)
    line(d,(64,494,1216,494))
    text(d,(64,525),'SCAN  /  DEEP READ  /  EVIDENCE',24,ACCENT,bold=True)
    text(d,(64,585),'github.com/zachsaws/podcast-xmind',23,MUTED)
    social.save(assets/'social-preview.png',optimize=True)

    hero='''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="480" viewBox="0 0 1280 480" role="img" aria-labelledby="title desc">
<title id="title">Podcast XMind</title><desc id="desc">Read the podcast. Keep the details. Source audio becomes a scan, a deep read and source evidence.</desc>
<rect width="1280" height="480" fill="#F4F0E6"/>
<path d="M60 77H1220M60 425H1220" stroke="#183C35" stroke-width="2"/>
<g font-family="Arial,Helvetica,sans-serif" fill="#183C35">
<text x="62" y="51" font-size="17" font-weight="700" letter-spacing="2">PX / AN AGENT SKILL FOR PODCAST READERS</text>
<text x="57" y="197" font-size="108" font-weight="700" letter-spacing="-4">Podcast</text>
<text x="57" y="306" font-size="108" font-weight="700" letter-spacing="-4">XMind<tspan fill="#B9472F">.</tspan></text>
<text x="63" y="373" font-size="23">READ THE PODCAST. KEEP THE DETAILS.</text>
<text x="62" y="455" font-size="15" fill="#55685C">Open source / Source-linked reading / Information ledgers</text>
<text x="982" y="455" font-size="15" fill="#55685C">zachsaws / podcast-xmind</text>
</g>
<g stroke="#B9472F" stroke-width="6" stroke-linecap="round">
<path d="M736 223V257M755 199V281M774 169V311M793 205V275M812 188V292"/>
</g>
<g fill="none" stroke="#183C35" stroke-width="2"><path d="M840 240H897M897 142V339M897 142H947M897 240H947M897 339H947"/></g>
<g fill="#B9472F"><circle cx="947" cy="142" r="5"/><circle cx="947" cy="240" r="5"/><circle cx="947" cy="339" r="5"/></g>
<g font-family="Arial,Helvetica,sans-serif" fill="#183C35" font-size="29" font-weight="700"><text x="972" y="142">Scan</text><text x="972" y="240">Deep read</text><text x="972" y="339">Evidence</text></g>
<g font-family="Arial,Helvetica,sans-serif" fill="#55685C" font-size="16"><text x="972" y="168">Find your way in.</text><text x="972" y="266">Follow the reasoning.</text><text x="972" y="365">Go back to the source.</text></g></svg>'''
    (assets/'cover.svg').write_text(hero,encoding='utf-8')
    print('Built cover.svg, evidence-tour.png, evidence-tour.gif, social-preview.png')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font');parser.add_argument('--bold-font')
    args=parser.parse_args()
    build(font_path(args.font),font_path(args.bold_font,True))
