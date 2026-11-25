#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Build the slot 7 data book and the two-page digest as PDF from the Markdown documentation.

    python3 docs/chipalooza2_as_taped_out/book/build_book.py [--sha <commit>] [--check-only]

Needs pandoc (3.x) and WeasyPrint (tested with 70.0). Steps:
  1. each Markdown file of BOOK is converted by pandoc (gfm reader, GitHub heading identifiers) to a JSON AST;
  2. identifiers are prefixed per file; a link to a file that is part of the book becomes an internal link, every other
     relative link becomes a GitHub link pinned to the source commit; images are resolved to local files;
  3. figure galleries are added for plots / schematics / layouts that the text links to but does not embed;
  4. cover, summary, table of contents (with page numbers) and the chapters go into one HTML file, which WeasyPrint
     turns into a PDF with bookmarks.
Every internal link is checked against the identifiers in the book; every relative link against the repository.
Problems are printed and written to book/build_report.txt; --check-only stops after the checks.
"""
import argparse, datetime, html, json, os, re, subprocess, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DOCS = 'docs/chipalooza2_as_taped_out'
REPO_URL = 'https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7'
OUT_DIR = os.path.join(ROOT, DOCS, 'pdf')
VG = 'verification/c2_gaps'

# (part title, [(file, gallery spec or None, include h2 in TOC)])
# gallery spec: (image glob roots relative to ROOT, caption source files)
GAP_FOLDERS = ['d2s_pex', 'replica_bias', 'slot_modes_bg', 'dc_curves', 'ac_tran', 'd2s_schematic_rerun',
               's2d_mismatch', 'klayout_pad_diodes']
BOOK = [
    ('Part I — Description', [
        (f'{DOCS}/README.md#body', None, True),
        (f'{DOCS}/HOW_IT_WORKS.md', None, True),
        (f'{DOCS}/glue_logic.md', None, True),
    ]),
    ('Part II — Data sheets', [
        (f'{DOCS}/datasheets/README.md', None, False),
        (f'{DOCS}/datasheets/sg13cmos5l_IOPadSingle2Diff.md', None, True),
        (f'{DOCS}/datasheets/sg13cmos5l_IOPadDiff2Single.md', None, True),
        (f'{DOCS}/datasheets/pad_ref_rb.md', None, True),
        (f'{DOCS}/datasheets/en_ctrl_3v3_level_shifter.md', None, True),
        (f'{DOCS}/datasheets/slot_7_system.md', None, True),
    ]),
    ('Part III — Working limits and test plan', [
        (f'{DOCS}/ACHIEVED_VS_LIMITS.md', None, True),
        (f'{DOCS}/TEST_PLAN.md', None, True),
        (f'{DOCS}/test_platforms.md', None, True),
    ]),
    ('Appendix A — Gap simulations after the tapeout', [
        x for g in GAP_FOLDERS for x in (
            [(f'{VG}/{g}/README.md', None, False),
             (f'{VG}/{g}/results.md', ([f'{VG}/{g}'], [f'{VG}/{g}/README.md', f'{VG}/{g}/results.md']), False)]
            if os.path.exists(os.path.join(ROOT, VG, g, 'results.md')) else
            [(f'{VG}/{g}/README.md', ([f'{VG}/{g}'], [f'{VG}/{g}/README.md']), False)])
    ]),
    ('Appendix B — Sign-off', [
        ('signoff/README.md', None, False),
        ('signoff/taped_out_158afc5/README.md', None, False),
    ]),
    ('Appendix C — Schematics', [
        (f'{DOCS}/pix/schematics/README.md', ([f'{DOCS}/pix/schematics'], [f'{DOCS}/pix/schematics/README.md']), False),
        (f'{DOCS}/pix/schematics/testbenches/README.md',
         ([f'{DOCS}/pix/schematics/testbenches'], [f'{DOCS}/pix/schematics/testbenches/README.md']), False),
    ]),
    ('Appendix D — Layout', [
        (f'{DOCS}/pix/layout/README.md', ([f'{DOCS}/pix/layout'], [f'{DOCS}/pix/layout/README.md']), False),
    ]),
    ('Appendix E — Design-rationale plots', [
        (f'{DOCS}/pix/plots/README.md', ([f'{DOCS}/pix/plots'], [f'{DOCS}/pix/plots/README.md']), False),
    ]),
    ('Appendix F — Harness integration', [
        ('README.md', None, False),
        ('docs/FOR_TIM.md', None, False),
        ('docs/slot_7.md', None, False),
        ('docs/PROGRESS.md', None, False),
    ]),
    ('Appendix G — Chipalooza #2 rules', [
        ('docs/RULES_COMPLIANCE_chipalooza2.md', None, False),
    ]),
    ('Appendix H — How this documentation was made', [
        ('docs/AI_ASSISTANCE.md', None, False),
        (f'{DOCS}/log.md', None, False),
        (f'{DOCS}/characterization_candidates.md', None, False),
    ]),
    ('Appendix I — Chipalooza #2 proposal', [
        (f'{DOCS}/PROPOSAL_chipalooza2.md', None, False),
    ]),
]
SUMMARY_SRC = f'{DOCS}/README.md#summary'
SPLIT_HEADING = '1. Which version was taped out'   # README: everything before this heading is the summary

problems = []
problems_info = []   # not errors; listed in the report
BRANCH = 'chipalooza2-documentation'


def problem(msg):
    problems.append(msg)


def sh(*cmd, inp=None):
    r = subprocess.run(cmd, input=inp, capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(f'{" ".join(cmd)} failed:\n{r.stderr}')
    return r.stdout


def slug(path):
    return re.sub(r'[^A-Za-z0-9]+', '-', path.replace('.md', '')).strip('-').lower()


def walk(x, fn):
    """Depth-first walk over a pandoc JSON AST; fn(node) may modify dict nodes in place."""
    if isinstance(x, dict):
        fn(x)
        for v in x.values():
            walk(v, fn)
    elif isinstance(x, list):
        for v in x:
            walk(v, fn)


def stringify(inl):
    out = []

    def f(n):
        t = n.get('t')
        if t == 'Str':
            out.append(n['c'])
        elif t in ('Space', 'SoftBreak', 'LineBreak'):
            out.append(' ')
        elif t == 'Code':
            out.append(n['c'][1])
        elif t == 'Math':
            out.append(n['c'][1])
    walk(inl, f)
    return ''.join(out)


class Book:
    def __init__(self, sha):
        self.sha = sha
        self.files = {}           # path -> slug (files that are in the book)
        self.ids = set()          # all identifiers in the book
        self.links = []           # (source file, internal target id) for checking
        self.embedded = set()     # absolute image paths shown somewhere in the book
        for _, items in BOOK:
            for f, _, _ in items:
                self.files[f.split('#')[0]] = slug(f.split('#')[0])

    def gh(self, path, frag=''):
        p = os.path.join(ROOT, path)
        kind = 'tree' if os.path.isdir(p) else 'blob'
        ref = self.sha
        if subprocess.run(['git', 'cat-file', '-e', f'{self.sha}:{path.rstrip("/")}'], cwd=ROOT,
                          capture_output=True).returncode:
            # not in the source commit (e.g. the PDFs themselves, committed after it): link to the branch
            ref = BRANCH
            note = f'link to {path}: not in {self.sha[:7]}, linked to branch {BRANCH}'
            if note not in problems_info:
                problems_info.append(note)
        return f'{REPO_URL}/{kind}/{ref}/{urllib.parse.quote(path.rstrip("/"))}' + (f'#{frag}' if frag else '')

    def resolve_link(self, src, url):
        if re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I):
            return url
        path, _, frag = url.partition('#')
        if not path:
            return f'#{self.files[src]}--{frag}' if frag else f'#{self.files[src]}'
        target = os.path.normpath(os.path.join(os.path.dirname(src), urllib.parse.unquote(path)))
        if target.startswith('..'):
            problem(f'{src}: link leaves the repository: {url}')
            return url
        full = os.path.join(ROOT, target)
        if not os.path.exists(full):
            problem(f'{src}: link target does not exist: {url}')
            return self.gh(target, frag)
        if os.path.isdir(full) and os.path.join(target, 'README.md') in self.files and not frag:
            target = os.path.join(target, 'README.md')
        if target in self.files:
            s = self.files[target]
            iid = f'{s}--{frag}' if frag else s
            self.links.append((src, iid))
            return f'#{iid}'
        if target.endswith('.md') and os.path.isfile(full) and frag:
            # anchor into a file outside the book: check it against that file's GitHub identifiers
            if frag not in heading_ids(target):
                problem(f'{src}: anchor #{frag} not found in {target} (outside the book): {url}')
        return self.gh(target, frag)

    def convert(self, src, part=None):
        """Markdown file -> list of (html, toc entries) ; part: 'summary' / 'body' / None for README splitting."""
        md = open(os.path.join(ROOT, src), encoding='utf-8').read()
        md = re.sub(r'^<!--.*?-->\s*', '', md, flags=re.S)          # SPDX comment block
        ast = json.loads(sh('pandoc', '-f', 'gfm+footnotes', '-t', 'json', inp=md))
        s = self.files.get(src) or slug(src)
        self.files.setdefault(src, s)
        base = os.path.dirname(src)

        def fix(n):
            t = n.get('t')
            if t == 'Header':
                attr = n['c'][1]
                attr[0] = f'{s}--{attr[0]}' if attr[0] else ''
            elif t in ('Div', 'Span', 'CodeBlock', 'Code'):
                attr = n['c'][0]
                if attr[0]:
                    attr[0] = f'{s}--{attr[0]}'
            elif t == 'Link':
                n['c'][2][0] = self.resolve_link(src, n['c'][2][0])
            elif t == 'Image':
                url = n['c'][2][0]
                if not re.match(r'^[a-z]+:', url):
                    p = os.path.normpath(os.path.join(ROOT, base, urllib.parse.unquote(url)))
                    if not os.path.exists(p):
                        problem(f'{src}: image does not exist: {url}')
                    self.embedded.add(p)
                    n['c'][2][0] = 'file://' + p
        walk(ast['blocks'], fix)
        blocks = ast['blocks']
        if part:
            idx = next(i for i, b in enumerate(blocks)
                       if b['t'] == 'Header' and stringify(b['c'][2]).strip() == SPLIT_HEADING)
            blocks = blocks[:idx] if part == 'summary' else blocks[idx:]
        for b in blocks:
            if b['t'] == 'Header':
                self.ids.add(b['c'][1][0])
        walk(blocks, lambda n: self.ids.add(n['c'][0][0]) if n.get('t') in ('Div', 'Span') and n['c'][0][0] else None)
        heads = [(b['c'][0], b['c'][1][0], stringify(b['c'][2])) for b in blocks if b['t'] == 'Header']
        ast['blocks'] = blocks
        out = sh('pandoc', '-f', 'json', '-t', 'html5', '--wrap=none', inp=json.dumps(ast))
        return out, heads


_hid_cache = {}


def heading_ids(path):
    if path not in _hid_cache:
        md = open(os.path.join(ROOT, path), encoding='utf-8').read()
        ast = json.loads(sh('pandoc', '-f', 'gfm', '-t', 'json', inp=md))
        ids = set()
        walk(ast['blocks'], lambda n: ids.add(n['c'][1][0]) if n.get('t') == 'Header' else None)
        _hid_cache[path] = ids
    return _hid_cache[path]


def gallery(book, roots, caption_files, gid):
    """Figures for every image under roots that the book does not embed yet; caption from the folders' text."""
    imgs = []
    for r in roots:
        for dp, dn, fn in os.walk(os.path.join(ROOT, r)):
            dn[:] = sorted(d for d in dn if not d.startswith(('_', '.')) and d != 'testbenches' or
                           os.path.join(dp, d).endswith('testbenches') and 'testbenches' in r)
            for f in sorted(fn):
                if f.endswith(('.png', '.svg')):
                    imgs.append(os.path.join(dp, f))
    # an SVG and a PNG of the same plot: keep the PNG unless only the SVG exists
    names = {os.path.splitext(p)[0] for p in imgs if p.endswith('.png')}
    imgs = [p for p in imgs if p.endswith('.png') or os.path.splitext(p)[0] not in names]
    imgs = [p for p in imgs if p not in book.embedded]
    if not imgs:
        return ''
    text = '\n'.join(open(os.path.join(ROOT, c), encoding='utf-8').read() for c in caption_files if
                     os.path.exists(os.path.join(ROOT, c)))
    out = [f'<section class="gallery" id="{gid}"><h2 class="gallery-title">Figures of this folder not embedded in the '
           f'text above ({len(imgs)})</h2>']
    for p in imgs:
        rel = os.path.relpath(p, ROOT)
        name = os.path.basename(p)
        stem = os.path.splitext(name)[0]
        cap = ''
        for line in text.splitlines():
            if (name in line or f'{stem}.' in line or f'{stem}`' in line) and len(line) < 1200:
                cells = [c.strip() for c in line.strip().strip('|').split('|')] if line.lstrip().startswith('|') else [line.strip(' -*')]
                cells = [c for c in cells if c and name not in c and f'{stem}.' not in c and not re.fullmatch(r'`?[\w./*-]+`?', c)]
                if cells:
                    cap = ' — '.join(cells)
                    break
        cap_html = sh('pandoc', '-f', 'gfm', '-t', 'html5', '--wrap=none', inp=cap).strip() if cap else ''
        cap_html = re.sub(r'^<p>|</p>$', '', cap_html)
        cap_html = re.sub(r'<a href="[^"]*">(.*?)</a>', r'\1', cap_html)   # relative links in captions: text only
        out.append(f'<figure class="gal"><img src="file://{p}"/><figcaption><a href="{book.gh(rel)}"><code>{html.escape(rel)}</code></a>'
                   + (f'<br/>{cap_html}' if cap_html else '') + '</figcaption></figure>')
        book.embedded.add(p)
    out.append('</section>')
    return '\n'.join(out)


CSS = r'''
@page { size: A4; margin: 17mm 13mm 15mm 13mm;
  @top-left { content: string(chapter); font-size: 7pt; color: #555; }
  @top-right { content: "Slot 7 data book"; font-size: 7pt; color: #555; }
  @bottom-left { content: "Chipalooza #2 (IHP SG13CMOS5L), slot 7 — documentation @ SHORTSHA"; font-size: 7pt; color: #555; }
  @bottom-right { content: counter(page) " / " counter(pages); font-size: 7pt; color: #555; } }
@page cover { @top-left { content: none } @top-right { content: none } @bottom-left { content: none } @bottom-right { content: none } }
@page :first { @top-left { content: none } @top-right { content: none } }
html { font-family: "DejaVu Sans", sans-serif; font-size: 8.6pt; line-height: 1.33; color: #111; }
body { margin: 0; }
a { color: #0645ad; text-decoration: none; }
h1, h2, h3, h4 { line-height: 1.2; page-break-after: avoid; break-after: avoid; }
h1 { font-size: 15pt; margin: 0 0 4pt 0; string-set: chapter content(); bookmark-level: 2; }
h2 { font-size: 11.5pt; margin: 12pt 0 4pt; bookmark-level: 3; border-bottom: 0.5pt solid #bbb; }
h3 { font-size: 9.8pt; margin: 9pt 0 3pt; bookmark-level: 4; }
h4, h5, h6 { font-size: 9pt; margin: 7pt 0 2pt; bookmark-level: none; }
.chapter { break-before: page; }
.chapter .src { font-size: 7pt; color: #555; margin: 0 0 8pt 0; }
/* manual page breaks (heading ids, after the file prefix) */
.chapter h2[id$="--7-aside-the-tughra"], .chapter h2[id$="--8-about-this-document-set"],
.chapter h3[id$="--62-fail-safe-enables-ls_up_fs"],
.chapter h2[id$="glue-logic--7-what-was-verified-and-what-was-not"] { break-before: page; }
.part { break-before: page; padding-top: 70mm; }
.part h1.part-title { font-size: 22pt; bookmark-level: 1; string-set: chapter content(); border: none; }
.part p { font-size: 9.5pt; max-width: 140mm; }
p { margin: 3pt 0; orphans: 2; widows: 2; }
ul, ol { margin: 2pt 0 2pt 0; padding-left: 14pt; }
li { margin: 1pt 0; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt; overflow-wrap: anywhere; }
pre { font-size: 6.9pt; line-height: 1.22; background: #f6f6f6; border: 0.4pt solid #ddd; padding: 3pt 4pt;
      white-space: pre-wrap; overflow-wrap: anywhere; }
pre code { font-size: inherit; }
table { border-collapse: collapse; margin: 4pt 0; font-size: 7pt; line-height: 1.22; width: 100%; }
th, td { border: 0.4pt solid #999; padding: 1.2pt 2.5pt; vertical-align: top; overflow-wrap: break-word; }
td code { overflow-wrap: break-word; }
th { background: #e9eef4; text-align: left; }
tr { break-inside: avoid; }
img { max-width: 100%; max-height: 225mm; }
p > img:only-child { display: block; margin: 4pt auto; }
p:has(> img) { break-inside: avoid; }
em { }
blockquote { margin: 4pt 0 4pt 8pt; padding-left: 6pt; border-left: 2pt solid #ccc; color: #333; }
details, summary { display: block; }
summary { font-style: italic; margin-top: 4pt; }
.gallery-title { break-before: page; }
figure.gal { margin: 6pt 0 10pt 0; break-inside: avoid; text-align: center; }
figure.gal img { max-height: 200mm; }
figure.gal figcaption { font-size: 7.4pt; text-align: left; margin-top: 2pt; }
/* cover */
.cover { page: cover; padding-top: 30mm; }
.cover h1 { font-size: 24pt; string-set: chapter ""; bookmark-level: 1; line-height: 1.15; }
.cover .sub { font-size: 13pt; margin: 6pt 0 18pt; color: #333; }
.cover table { font-size: 8.5pt; width: auto; }
.cover td { border: none; padding: 2pt 10pt 2pt 0; }
.cover .note { margin-top: 18pt; font-size: 9pt; border: 0.6pt solid #c90; background: #fff8e6; padding: 6pt; }
/* summary and toc */
.summary { break-before: page; }
.summary h1 { bookmark-level: 1; }
.summary img { max-height: 72mm; }
.summary h2[id$="--where-to-find-what"] { break-before: page; }
.summary h2[id$="--where-to-find-what"] + table { break-inside: avoid; }
.summary p:has(> img) { text-align: center; margin: 2pt 0 0 0; }
.toc { break-before: page; }
.toc h1 { bookmark-level: 1; }
.toc ul { list-style: none; padding-left: 0; margin: 0; }
.toc li { margin: 0; }
.toc li.tp { font-weight: bold; font-size: 9.6pt; margin-top: 7pt; }
.toc li.ch { padding-left: 8pt; font-size: 8.6pt; margin-top: 1.5pt; }
.toc li.h2 { padding-left: 20pt; font-size: 7.6pt; color: #222; }
.toc li a { color: #111; }
.toc li a::after { content: leader('.') target-counter(attr(href url), page); }
'''


def build_book(sha, check_only):
    book = Book(sha)
    short = sha[:7]
    chapters_html, toc = [], []

    summary_html, _ = book.convert(f'{DOCS}/README.md', part='summary')
    first = True
    for pi, (ptitle, items) in enumerate(BOOK):
        pid = f'part-{pi}'
        book.ids.add(pid)
        toc.append(('tp', pid, ptitle))
        intro = PART_INTRO.get(ptitle, '')
        chapters_html.append(f'<section class="part"><h1 class="part-title" id="{pid}">{html.escape(ptitle)}</h1>{intro}</section>')
        for f, gal, toc_h2 in items:
            path, _, sel = f.partition('#')
            h, heads = book.convert(path, part=sel or None)
            s = book.files[path]
            cid = s if sel != 'body' else f'{s}--body'
            book.ids.add(cid)
            if sel == 'body':
                title = 'Slot 7 as taped out: description (§1 – §8)'
                h = f'<h1>{title}</h1>' + h
            else:
                title = heads[0][2] if heads and heads[0][0] == 1 else os.path.basename(path)
            toc.append(('ch', cid, title))
            if toc_h2:
                toc += [('h2', i, t) for lvl, i, t in heads if lvl == 2]
            src_line = (f'<p class="src">Source: <a href="{book.gh(path)}"><code>{html.escape(path)}</code></a> '
                        f'at commit <code>{short}</code></p>')
            # put the anchor of the file on the chapter, the source line after its first heading
            h = re.sub(r'(</h1>)', r'\1' + src_line.replace('\\', r'\\'), h, count=1) if '<h1' in h else src_line + h
            g = gallery(book, *gal, gid=f'{s}--gallery') if gal else ''
            chapters_html.append(f'<section class="chapter" id="{cid}">{h}{g}</section>')
    # README summary part: its own anchor is the README slug (links to README.md land on the summary)
    book.ids.add(book.files[f'{DOCS}/README.md'])

    missing = sorted({(s, i) for s, i in book.links if i not in book.ids})
    for s, i in missing:
        problem(f'{s}: internal anchor not found in the book: #{i}')
    report = os.path.join(HERE, 'build_report.txt')
    with open(report, 'w') as fh:
        fh.write(f'# build_book.py report, source commit {sha}\n' + ''.join(p + '\n' for p in problems)
                 + ''.join(f'note: {p}\n' for p in problems_info))
    print(f'{len(problems)} problem(s); see {os.path.relpath(report, ROOT)}')
    for p in problems:
        print('  ' + p)
    if check_only:
        return

    toc_html = ['<section class="toc"><h1 id="toc">Contents</h1><ul>']
    for kind, i, t in toc:
        toc_html.append(f'<li class="{kind}"><a href="#{i}">{html.escape(t)}</a></li>')
    toc_html.append('</ul></section>')

    date = datetime.date.today().isoformat()
    cover = COVER.format(sha=sha, short=short, date=date, repo=REPO_URL)
    summary = (f'<section class="summary" id="{book.files[f"{DOCS}/README.md"]}">'
               + summary_html.replace('<h2 ', '<h2 ', 1) + '</section>')
    summary = re.sub(r'<h1[^>]*>.*?</h1>', '<h1 id="summary">Summary: slot 7 at a glance</h1>', summary, count=1, flags=re.S)
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Slot 7 data book</title>'
           f'<meta name="author" content="Christoph Maier"><style>{CSS.replace("SHORTSHA", short)}</style></head><body>'
           + cover + summary + ''.join(toc_html) + ''.join(chapters_html) + '</body></html>')
    os.makedirs(OUT_DIR, exist_ok=True)
    html_path = os.path.join(HERE, '_build', 'slot7_databook.html')
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    open(html_path, 'w', encoding='utf-8').write(doc)
    import weasyprint
    pdf = os.path.join(OUT_DIR, 'slot7_databook.pdf')
    weasyprint.HTML(html_path, base_url=ROOT).write_pdf(pdf)
    print(f'wrote {os.path.relpath(pdf, ROOT)}')


PART_INTRO = {
    'Part I — Description':
        '<p>What slot 7 is, how it works and how it is controlled: the taped-out version, signal and current flow, the blocks, '
        'supplies and modes; the design rationale with equations and sizing tables; the 3.3 V glue logic.</p>',
    'Part II — Data sheets':
        '<p>One data sheet per pad, for the replica bias, the enable level shifter and the whole slot. All values are '
        'simulations; the limits are the working limits of an ad hoc specification written during the AI-assisted design, which the design does not quite meet.</p>',
    'Part III — Working limits and test plan':
        '<p>What was achieved against the working limits, how to measure the chip, and the earlier test platforms that were '
        'not taped out.</p>',
    'Appendix A — Gap simulations after the tapeout':
        '<p>Simulations made after the tapeout (2026-11-23 … 2026-11-25) to close gaps of the characterization. Each '
        'folder: README (question, method, how to reproduce) and results; the figures follow each results chapter. The '
        'CSV files behind the figures stay in the repository and are not reprinted here.</p>',
    'Appendix B — Sign-off':
        '<p>DRC and LVS of the blocks as committed by the designer, and the re-run of the sign-off on the taped-out GDS.</p>',
    'Appendix C — Schematics':
        '<p>xschem sheets of the taped-out blocks and the test benches, rendered to SVG from the design repository at the '
        'taped-out commits.</p>',
    'Appendix D — Layout': '<p>KLayout renders of the taped-out GDS.</p>',
    'Appendix E — Design-rationale plots': '<p>Plots made from committed data for the design-rationale chapter.</p>',
    'Appendix F — Harness integration':
        '<p>The repository README (files the harness reads, provenance, pin table) and the notes written for the harness '
        'owner at hand-over.</p>',
    'Appendix G — Chipalooza #2 rules': '<p>Slot 7 against each item of the Chipalooza #2 rules.</p>',
    'Appendix I — Chipalooza #2 proposal':
        '<p>The proposal for slot 7 as submitted (10 August 2026), unchanged.</p>',
    'Appendix H — How this documentation was made':
        '<p>AI assistance, the running log of the documentation session of 2026-11-22 and the inventory of '
        'characterization data it started from.</p>',
}

COVER = '''<section class="cover">
<h1>Slot 7: custom S2D / D2S pad pair with a bandgap-referenced replica bias</h1>
<p class="sub">Data book — Chipalooza Challenge #2 (IHP SG13CMOS5L), slot 7, as taped out on 2026-11-09</p>
<table>
<tr><td>Designer</td><td>Christoph Maier</td></tr>
<tr><td>Taped-out design</td><td>commit <code>158afc5</code> of <a href="{repo}">{repo}</a></td></tr>
<tr><td>This documentation</td><td>branch <code>chipalooza2-documentation</code>, commit <a href="{repo}/tree/{sha}"><code>{short}</code></a></td></tr>
<tr><td>Built</td><td>{date}, from the Markdown files of that commit (<code>docs/chipalooza2_as_taped_out/book/build_book.py</code>)</td></tr>
<tr><td>License</td><td>repository <code>LICENSE</code>: Solderpad Hardware License 2.1; the documentation files carry <code>SPDX-License-Identifier: Apache-2.0</code> (Appendix G, item 14)</td></tr>
</table>
<p class="note">No silicon results exist yet. Every number in this book is a simulation (IHP SG13CMOS5L, ngspice, schematic or
extracted layout as stated). The specification is an ad hoc one, the working limits written during the AI-assisted
design; the taped-out design does not quite meet it (Part III).</p>
<p style="margin-top:14pt;font-size:8.5pt">How to read it: the summary (next pages) gives the slot with its main figures and numbers; the
contents list is clickable, and so is every cross-reference. Links into files that are not reprinted here (scripts, CSV
files, netlists) open the file on GitHub at the commit above.</p>
</section>'''


DIGEST_SRC = f'{DOCS}/DIGEST.md'
DIGEST_CSS = r'''
@page { size: A4; margin: 13mm 14mm 13mm 14mm;
  @bottom-left { content: "Chipalooza #2 (IHP SG13CMOS5L), slot 7 — documentation @ SHORTSHA"; font-size: 7pt; color: #666; }
  @bottom-right { content: counter(page) " / " counter(pages); font-size: 7pt; color: #666; } }
html { font-family: "DejaVu Sans", sans-serif; font-size: 8.9pt; line-height: 1.34; color: #111; }
body { margin: 0; }
a { color: #0645ad; text-decoration: none; }
h1 { font-size: 17pt; margin: 0 0 3pt 0; }
h2 { font-size: 11pt; margin: 9pt 0 3pt; border-bottom: 0.5pt solid #bbb; break-after: avoid; }
p { margin: 3pt 0; }
ul, ol { margin: 2pt 0; padding-left: 14pt; }
li { margin: 1.2pt 0; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0; font-size: 8.3pt; }
th, td { border: 0.4pt solid #aaa; padding: 1.6pt 4pt; vertical-align: top; }
th { background: #e9eef4; text-align: left; }
img { max-width: 100%; }
p > img:only-child { display: block; margin: 3pt auto; max-height: 60mm; }
p > img[src$=".svg"]:only-child { width: 100%; }
p > em:only-child { font-size: 7.6pt; }
tr { break-inside: avoid; }
h2 + table, h2 + p { break-before: avoid; }
blockquote { margin: 5pt 0; padding: 4pt 7pt; border: 0.6pt solid #9bb; background: #f1f7f7; }
blockquote p { margin: 0; }
table.figs { table-layout: fixed; }
table.figs td { border: none; width: 50%; font-size: 7.6pt; padding: 0 3pt; text-align: left; }
table.figs td img { max-width: 80%; max-height: 85mm; }
table.figs th { display: none; }
'''


def build_digest(sha):
    book = Book(sha)
    book.files = {}                                   # the digest stands alone: every link goes to GitHub
    # the digest is a data sheet of the circuit: no die art, no history of the art
    md = open(os.path.join(ROOT, DIGEST_SRC), encoding='utf-8').read()
    if re.search(r'tughra|art/|calligraph|latent', md, re.I):
        sys.exit(f'{DIGEST_SRC} mentions the die art; the digest covers the circuit only')
    h, _ = book.convert(DIGEST_SRC)
    # tables that hold images are figure grids (no borders, equal columns); all others are data tables
    h = re.sub(r'<table>(?=(?:(?!</table>).)*?<img)', '<table class="figs">', h, flags=re.S)
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Slot 7 in two pages</title>'
           f'<meta name="author" content="Christoph Maier"><style>{DIGEST_CSS.replace("SHORTSHA", sha[:7])}</style></head>'
           f'<body>{h}</body></html>')
    import weasyprint
    pdf = os.path.join(OUT_DIR, 'slot7_digest.pdf')
    os.makedirs(OUT_DIR, exist_ok=True)
    weasyprint.HTML(string=doc, base_url=ROOT).write_pdf(pdf)
    print(f'wrote {os.path.relpath(pdf, ROOT)}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sha', help='source commit for the pinned GitHub links (default: HEAD)')
    ap.add_argument('--check-only', action='store_true')
    ap.add_argument('--digest-only', action='store_true')
    a = ap.parse_args()
    sha = a.sha or sh('git', 'rev-parse', 'HEAD').strip()
    dirty = sh('git', 'status', '--porcelain', '--', 'docs', 'verification', 'signoff', 'README.md')
    if dirty.strip():
        print('warning: uncommitted documentation changes; the pinned links point to ' + sha[:7] + ':\n' + dirty)
    if not a.digest_only:
        build_book(sha, a.check_only)
    if not a.check_only:
        build_digest(sha)
        if a.digest_only:
            for p in problems:
                print('  ' + p)


if __name__ == '__main__':
    main()
