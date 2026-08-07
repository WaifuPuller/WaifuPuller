"""Thorough test pass for the arlecchino_os generator.

Covers: XML validity, special-character escaping, long values,
boot-line counts, and the portrait pipeline across image formats,
color modes, and extreme sizes.
"""
import copy
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import generate as g  # noqa: E402

from PIL import Image  # noqa: E402

SCRATCH = Path(tempfile.mkdtemp(prefix="arlecchino-tests-"))

passed, failed = 0, 0


def run(label, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"  PASS  {label}")
    except Exception as e:  # noqa: BLE001
        failed += 1
        print(f"  FAIL  {label}: {type(e).__name__}: {e}")


def valid_svg(svg: str):
    # parse as bytes: the documents carry an encoding declaration, and
    # this is exactly how a browser will read them
    ET.fromstring(svg.encode("utf-8"))  # raises on malformed XML
    assert svg.startswith("<?xml"), "missing XML/encoding declaration"
    assert "http://" not in svg.replace("http://www.w3.org", ""), \
        "external resource reference found (won't load in GitHub <img>)"


base = g.load_config()

# ---- 1. baseline -------------------------------------------------
run("baseline placeholder hero is valid XML, no external refs",
    lambda: valid_svg(g.build_hero(base, None)))

# ---- 2. special characters ---------------------------------------
def special_chars():
    c = copy.deepcopy(base)
    c["identity"]["name"] = 'K&mar <script> "quotes" \'apos\''
    c["identity"]["role"] = "R&D <lead>"
    c["identity"]["tagline"] = 'building <fast> & "quiet"'
    c["identity"]["status_note"] = "a & b <c>"
    c["identity"]["handle"] = "k&m"
    c["portrait"]["label"] = "<arl&e>"
    c["os"]["title"] = "os & <co>"
    c["boot"]["lines"] = ['load & <mount> ... "ok"']
    svg = g.build_hero(c, None)
    valid_svg(svg)
    assert "<script>" not in svg
run("special characters escaped everywhere", special_chars)

# ---- 3. unicode / emoji ------------------------------------------
def unicode_vals():
    c = copy.deepcopy(base)
    c["identity"]["name"] = "Kúmär Bütchà 星"
    c["identity"]["status_note"] = "café ☕ mode"
    valid_svg(g.build_hero(c, None))
run("unicode + emoji values", unicode_vals)

# ---- 4. long values ----------------------------------------------
def long_vals():
    c = copy.deepcopy(base)
    c["identity"]["name"] = "An Extremely Long Display Name That Never Ends"
    c["identity"]["status_note"] = "x" * 60
    valid_svg(g.build_hero(c, None))
run("very long name/status build without error", long_vals)

# ---- 5. boot line counts -----------------------------------------
def boot_counts():
    for n in (0, 1, 8):
        c = copy.deepcopy(base)
        c["boot"]["lines"] = [f"line {i}" for i in range(n)]
        valid_svg(g.build_hero(c, None))
run("0 / 1 / 8 boot lines", boot_counts)

# ---- 6. portrait pipeline: formats & modes ------------------------
def make_img(name, mode, size, fmt, **save_kw):
    img = Image.new(mode, size)
    if mode in ("RGB", "RGBA"):
        for x in range(0, size[0], max(1, size[0] // 40)):
            for y in range(0, size[1], max(1, size[1] // 40)):
                img.putpixel((x, y), (200, 60, 90, 255)[:len(img.getbands())])
    p = SCRATCH / name
    img.save(p, fmt, **save_kw)
    return p


def embed_ok(path):
    uri = g.embed_portrait(path, base)
    assert uri.startswith("data:image/jpeg;base64,")
    kb = len(uri) * 3 // 4 // 1024
    assert kb < 200, f"embedded image too heavy: {kb} KB"
    svg = g.build_hero(base, uri)
    valid_svg(svg)


run("PNG with alpha (RGBA)",   lambda: embed_ok(make_img("a.png", "RGBA", (1200, 1600), "PNG")))
run("palette PNG (mode P)",    lambda: embed_ok(make_img("p.png", "RGB", (900, 900), "PNG").parent / "p.png" if make_img("p2.png", "P", (900, 900), "PNG") else None) if False else embed_ok(make_img("p3.png", "P", (900, 900), "PNG")))
run("WebP",                    lambda: embed_ok(make_img("w.webp", "RGB", (1000, 700), "WEBP")))
run("grayscale JPEG (mode L)", lambda: embed_ok(make_img("g.jpg", "L", (800, 1200), "JPEG")))
run("tiny image 80x80 upscale path", lambda: embed_ok(make_img("t.png", "RGB", (80, 80), "PNG")))
run("huge image 6000x4000 downscale", lambda: embed_ok(make_img("h.jpg", "RGB", (6000, 4000), "JPEG", quality=70)))
run("extreme panorama 4000x400", lambda: embed_ok(make_img("pan.jpg", "RGB", (4000, 400), "JPEG")))
run("extreme tall 400x4000",   lambda: embed_ok(make_img("tall.jpg", "RGB", (400, 4000), "JPEG")))

# ---- 7. explorer -------------------------------------------------
run("explorer baseline valid", lambda: valid_svg(g.build_explorer(base)))


def explorer_special():
    c = copy.deepcopy(base)
    c["projects"][0].update(name="a&b <x>", desc='d & <e> "f"', type="<t&y>",
                            status="<live&loud>", stack=["C&C++", "<xml>"])
    svg = g.build_explorer(c)
    valid_svg(svg)
    assert "<x>" not in svg.replace("<xml", "")
run("explorer special characters", explorer_special)


def explorer_counts():
    for n in (1, 8, 12):
        c = copy.deepcopy(base)
        c["projects"] = [dict(base["projects"][0], name=f"proj-{i}") for i in range(n)]
        valid_svg(g.build_explorer(c))
    c = copy.deepcopy(base)
    c["projects"] = []
    assert g.build_explorer(c) == ""
run("explorer with 1 / 8 / 12 / 0 projects", explorer_counts)


def explorer_missing_fields():
    c = copy.deepcopy(base)
    c["projects"] = [{"name": "bare"}]  # every other field optional
    valid_svg(g.build_explorer(c))
run("explorer project with only a name", explorer_missing_fields)


def explorer_long_desc():
    c = copy.deepcopy(base)
    c["projects"][0]["desc"] = "word " * 80
    c["projects"][0]["stack"] = ["one", "two", "three", "four", "five", "six", "seven"]
    svg = g.build_explorer(c)
    valid_svg(svg)
run("explorer long description + many stack chips (clamped)", explorer_long_desc)

# ---- 8. packages / timeline / footer -----------------------------
run("packages baseline valid", lambda: valid_svg(g.build_packages(base)))
run("timeline baseline valid", lambda: valid_svg(g.build_timeline(base)))
run("footer baseline valid", lambda: valid_svg(g.build_footer(base)))


def panels_special():
    c = copy.deepcopy(base)
    c["skills"][0]["group"] = "l&ng <s>"
    c["skills"][0]["items"][0] = {"name": "C&C++ <v>", "channel": "we&ird"}
    c["timeline"][0].update(year="20&22", title="a <b> & c", detail='d "e" <f>')
    c["contact"]["email"] = "a&b@x.com"
    c["contact"]["links"] = [{"label": "<gh&>", "url": "https://x.com/<a&b>"}]
    for fn in (g.build_packages, g.build_timeline, g.build_footer):
        valid_svg(fn(c))
run("panels: special characters", panels_special)


def panels_empty_and_overflow():
    c = copy.deepcopy(base)
    c["skills"], c["timeline"], c["contact"] = [], [], {}
    assert g.build_packages(c) == ""
    assert g.build_timeline(c) == ""
    valid_svg(g.build_footer(c))  # footer with no entries still renders EOF
    c2 = copy.deepcopy(base)
    c2["skills"] = [dict(group=f"g{i}", items=[{"name": "x"}] * 15) for i in range(5)]
    c2["timeline"] = [dict(year=2000 + i, title=f"t{i}", detail="d") for i in range(12)]
    valid_svg(g.build_packages(c2))   # trims to 3 groups / 10 items
    valid_svg(g.build_timeline(c2))   # trims to 7 entries
run("panels: empty configs and overflow trimming", panels_empty_and_overflow)


# ---- 9. live data -------------------------------------------------
def live_data_disabled():
    c = copy.deepcopy(base)          # explicit, not inherited from config
    c["data"]["github_api"] = False
    assert g.fetch_github(c) is None
    c["data"] = {}                   # missing flag must also mean "off"
    assert g.fetch_github(c) is None
run("live data: disabled flag returns None", live_data_disabled)


def live_data_bad_user():
    c = copy.deepcopy(base)
    c["data"]["github_api"] = True
    c["identity"]["github_username"] = "this-user-should-not-exist-xyz-00193"
    assert g.fetch_github(c) is None  # 404 -> graceful None, no exception
run("live data: nonexistent user degrades gracefully", live_data_bad_user)


def live_data_real():
    c = copy.deepcopy(base)
    c["data"]["github_api"] = True
    c["identity"]["github_username"] = "octocat"
    live = g.fetch_github(c)
    if live is None:  # offline is acceptable, wrong shape is not
        print("        (network unavailable — skipped real fetch)")
        return
    assert live["public_repos"] > 0 and "repo_stars" in live
    valid_svg(g.build_explorer(c, live))
run("live data: real fetch (octocat) + explorer integration", live_data_real)

# ---- 10. hidden layers -------------------------------------------
run("manual page valid", lambda: valid_svg(g.build_manual(base)))
run("system info valid", lambda: valid_svg(g.build_system(base)))
run("secret panel valid", lambda: valid_svg(g.build_secret(base)))


def hidden_special():
    c = copy.deepcopy(base)
    c["hidden"]["manual"]["sections"] = [{"heading": "N&ME <x>",
                                          "lines": ['a & b "c" <d>']}]
    c["hidden"]["system"]["specs"] = [{"key": "e&d <x>", "value": 'v & "w"'}]
    c["hidden"]["secret"]["fortunes"] = ['a & b <c> "d"']
    for fn in (g.build_manual, g.build_system, g.build_secret):
        valid_svg(fn(c))
run("hidden layers: special characters", hidden_special)


def hidden_empty():
    c = copy.deepcopy(base)
    c["hidden"] = {}
    assert g.build_manual(c) == g.build_system(c) == g.build_secret(c) == ""
    c2 = copy.deepcopy(base)
    del c2["hidden"]
    assert g.build_manual(c2) == "" and g.build_secret(c2) == ""
run("hidden layers: absent config returns empty (no crash)", hidden_empty)


def hidden_overflow():
    c = copy.deepcopy(base)
    c["hidden"]["manual"]["sections"] = [
        {"heading": f"H{i}", "lines": [f"line {j}" for j in range(9)]}
        for i in range(8)
    ]
    c["hidden"]["system"]["specs"] = [{"key": f"k{i}", "value": "v"} for i in range(20)]
    c["hidden"]["secret"]["fortunes"] = ["word " * 60]
    for fn in (g.build_manual, g.build_system, g.build_secret):
        valid_svg(fn(c))
run("hidden layers: oversized config trims safely", hidden_overflow)


def fortune_rotates():
    fortunes = base["hidden"]["secret"]["fortunes"]
    picks = {g.day_index(len(fortunes)) for _ in range(3)}
    assert len(picks) == 1, "day_index must be stable within a day"
    assert 0 <= picks.pop() < len(fortunes)
run("daily rotation is stable and in range", fortune_rotates)


# ---- 11. README structure ----------------------------------------
def readme_structure():
    sections = [("hero", "h"), ("explorer", "e")]
    hidden = [("manual", "man arlecchino", "manual")]
    tail = [("footer", "c")]
    md = g.build_readme(base, sections, hidden, tail)
    assert md.count("<details>") == 1 and md.count("</details>") == 1
    assert md.index("output/hero.svg") < md.index("<details>") < md.index("output/footer.svg"), \
        "hidden blocks must sit between the visible stack and the footer"
    # markdown links are NOT parsed inside HTML blocks -> must be raw <a>
    assert "](mailto:" not in md and '<a href="mailto:' in md
    assert md.lstrip().startswith("<!--")  # source easter egg survives
run("README: details order, raw anchors, source egg", readme_structure)


def readme_no_contact():
    c = copy.deepcopy(base)
    c["contact"] = {}
    md = g.build_readme(c, [("hero", "h")], [], [])
    assert "<a href" not in md and "<details>" not in md
run("README: no contact / no hidden panels degrades cleanly", readme_no_contact)

# ---- 12. configurable labels -------------------------------------
def labels_reach_output():
    c = copy.deepcopy(base)
    c["labels"] = {
        "explorer": {"title": "WORKBENCH", "right": "/data", "root": "/data",
                     "footer": "{count} things · {os}"},
        "packages": {"title": "TOOLCHAIN", "command": "env list",
                     "right": "env v{version}", "footer": "{count} tools"},
        "timeline": {"title": "CHANGELOG", "right": "log"},
        "manual": {"title": "READMEPAGE", "right": "readme(1)"},
        "system": {"title": "WORKSTATION", "right": "specs"},
        "secret": {"title": "FIELDNOTES", "right": "less notes",
                   "intro": "hello there.", "note": "changes daily"},
        "contact": {"command": "reach --open", "email_label": "write",
                    "eof": "END · {os}"},
        "hero": {"prompt": "{handle}@atlas", "symbol": "›"},
    }
    out = "".join([g.build_hero(c, None), g.build_explorer(c), g.build_packages(c),
                   g.build_timeline(c), g.build_manual(c), g.build_system(c),
                   g.build_secret(c), g.build_footer(c)])
    valid_svg(g.build_explorer(c))
    for token in ("WORKBENCH", "TOOLCHAIN", "CHANGELOG", "READMEPAGE",
                  "WORKSTATION", "FIELDNOTES", "reach --open", "write",
                  "hello there.", "env list", "@atlas"):
        assert token in out, f"label not applied: {token}"
    # built-in wording must be gone once overridden
    for gone in ("repository_explorer", "package_manager", "system_log",
                 "manual_page", "system_info", "contact --open"):
        assert gone not in out, f"hardcoded wording leaked: {gone}"
run("labels: overrides applied, defaults replaced", labels_reach_output)


def labels_fallback():
    c = copy.deepcopy(base)
    c.pop("labels", None)
    out = g.build_explorer(c) + g.build_packages(c) + g.build_footer(c)
    assert "repository_explorer" in out and "package_manager" in out
    c["labels"] = {"explorer": {}}          # partial config
    valid_svg(g.build_explorer(c))
    c["labels"] = {"explorer": "not-a-dict"}  # wrong type must not crash
    valid_svg(g.build_explorer(c))
run("labels: missing / partial / wrong-typed configs fall back", labels_fallback)


def labels_hostile():
    c = copy.deepcopy(base)
    c["labels"] = {
        "explorer": {"title": "a & b <x>", "footer": 'f & "g" {unknown} {count}'},
        "secret": {"intro": "i & <j>", "note": "n & <o>"},
        "contact": {"eof": "e & <f> {os}", "email_label": "m&l"},
        "hero": {"prompt": "{handle} & <p>", "symbol": "&"},
    }
    for fn in (lambda x: g.build_hero(x, None), g.build_explorer,
               g.build_secret, g.build_footer):
        valid_svg(fn(c))
    # an unknown {token} must survive as literal text, never raise
    assert "{unknown}" in g.build_explorer(c)
run("labels: special characters and unknown tokens are safe", labels_hostile)


def readme_source_note():
    c = copy.deepcopy(base)
    c["readme"] = {"source_note": "  hello from the source  "}
    md = g.build_readme(c, [("hero", "h")], [], [])
    assert "<!--" in md and "hello from the source" in md
    c["readme"] = {"source_note": "sneaky --> <script>x</script>"}
    md = g.build_readme(c, [("hero", "h")], [], [])
    assert "<script>" not in md, "config must not break out of the HTML comment"
    c["readme"] = {}
    assert "<!--" not in g.build_readme(c, [("hero", "h")], [], [])
run("README: source note configurable, cannot escape the comment", readme_source_note)


def readme_src_prefix():
    md = g.build_readme(base, [("hero", "h")], [], [], src="examples/output")
    assert 'src="examples/output/hero.svg"' in md
run("README: output directory is relocatable", readme_src_prefix)


# ---- 13. the whole point: a second person, same code -------------
def second_persona():
    other = g.load_config(Path(g.ROOT) / "examples" / "atlas.yaml")
    assert other["identity"]["name"] != base["identity"]["name"]
    assert other["theme"]["accent"] != base["theme"]["accent"]
    panels = [g.build_hero(other, None), g.build_explorer(other),
              g.build_packages(other), g.build_timeline(other),
              g.build_manual(other), g.build_system(other),
              g.build_secret(other), g.build_footer(other)]
    for svg in panels:
        assert svg, "every panel must build for the second persona"
        valid_svg(svg)
    joined = "".join(panels)
    # none of the first persona's identity may appear anywhere
    for leak in ("arlecchino", "Kumar", "kumar", "repository_explorer",
                 "package_manager", "system_log"):
        assert leak not in joined, f"first persona leaked into second: {leak}"
run("two personas, one codebase — no identity leaks", second_persona)

# ---- 14. projects pulled live from GitHub ------------------------
FAKE_GH = {
    "followers": 3, "public_repos": 5, "stars": 9, "repo_stars": {},
    "repos": [
        {"name": "zzz-old", "desc": "", "language": "C", "topics": [],
         "stars": 0, "created": "2019", "pushed": "2019-01-01T00:00:00Z",
         "fork": False, "archived": False},
        {"name": "a-fork", "desc": "not mine", "language": "Go", "topics": [],
         "stars": 99, "created": "2024", "pushed": "2026-08-01T00:00:00Z",
         "fork": True, "archived": False},
        {"name": "shelved", "desc": "done", "language": "Rust", "topics": ["cli"],
         "stars": 4, "created": "2023", "pushed": "2026-08-01T00:00:00Z",
         "fork": False, "archived": True},
        {"name": "hot", "desc": "the good one", "language": "Python",
         "topics": ["ml", "data", "viz", "cli", "extra"], "stars": 9,
         "created": "2025", "pushed": "2026-08-06T00:00:00Z",
         "fork": False, "archived": False},
    ],
}


def auto_sorting_and_filtering():
    p = g.auto_projects(base, FAKE_GH)
    names = [x["name"] for x in p]
    assert "a-fork" not in names, "forks must be excluded"
    assert names[0] == "hot", "highest stars must lead"
    assert names == ["hot", "shelved", "zzz-old"], names
run("auto projects: forks dropped, ranked by stars then recency",
    auto_sorting_and_filtering)


def auto_field_mapping():
    p = {x["name"]: x for x in g.auto_projects(base, FAKE_GH)}
    assert p["shelved"]["status"] == "archived"
    assert p["zzz-old"]["status"] == "dormant", "stale repo must not read active"
    assert p["hot"]["status"] == "active"
    assert p["hot"]["type"] == "python" and p["hot"]["since"] == "2025"
    assert len(p["hot"]["stack"]) == 4, "topics capped to fit the panel"
    assert p["zzz-old"]["desc"], "a repo with no description still needs text"
    assert p["hot"]["stars"] == 9
run("auto projects: status, language, topics and empty descriptions",
    auto_field_mapping)


def auto_drives_explorer():
    c = copy.deepcopy(base)
    svg = g.build_explorer(c, FAKE_GH)
    valid_svg(svg)
    assert "hot" in svg
    for placeholder in ("campus-print", "counselling-platform", "playground"):
        assert placeholder not in svg, "config fallback must not win over live data"
    # and without live data the fallback keeps the panel alive
    assert "campus-print" in g.build_explorer(c, None)
run("auto projects: live data wins, config is the offline fallback",
    auto_drives_explorer)


def auto_hostile_repos():
    gh = {"repos": [
        {"name": "a&b <x>", "desc": 'd & "e" <f>', "language": "C&C++",
         "topics": ["<t&>"], "stars": 1, "created": "", "pushed": "garbage",
         "fork": False, "archived": False},
    ], "public_repos": 1, "stars": 1, "followers": 0, "repo_stars": {}}
    valid_svg(g.build_explorer(base, gh))       # bad date must not crash
    assert g.auto_projects(base, {"repos": []}) == []
    assert g.auto_projects(base, None) == []
run("auto projects: hostile names and unparseable dates are safe",
    auto_hostile_repos)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
