"""Optional release review for premium compositions (developer Playwright only).

Usage: python3 tests/premium_compositions_browser.py --browsers chromium firefox webkit --axe-file /tmp/axe.min.js
No browser or JavaScript runtime is needed by Syntyr consumers.
"""
import argparse
import os
from pathlib import Path
import shutil
import sys
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
URL=(ROOT/"examples/premium-compositions.html").as_uri()
RULE_TAGS=["wcag2a","wcag2aa","wcag21a","wcag21aa","wcag22aa"]


def chromium_launch_options():
    """Honor the optional system browser override used by the other suites."""
    opts = {"headless": True}
    executable = (os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                  or shutil.which("chromium") or shutil.which("chromium-browser"))
    if executable:
        opts["executable_path"] = executable
        opts["args"] = ["--no-sandbox"]
    return opts


def audit(browser, engine, axe_file):
    cases=0
    for width, scale in ((320,1),(320,2),(390,1),(390,2),(1280,1)):
        context=browser.new_context(viewport={"width":width,"height":860},reduced_motion="reduce")
        try:
            page=context.new_page()
            errors=[]
            page.on("pageerror",lambda ex: errors.append(str(ex)))
            page.goto(URL)
            assert page.locator("script").count()==0, (engine,"runtime script")
            assert page.get_by_role("main").count()==1, (engine,"main landmark")
            assert page.locator(".syn-activity-timeline time[datetime]").count()==3
            assert page.locator(".syn-command-row").count()==3
            page.evaluate("(s)=>document.documentElement.style.fontSize=(16*s)+'px'",scale)
            metrics=page.evaluate("""() => {
              const root=document.documentElement;
              const clipped=[...document.querySelectorAll('a,button,input,select,textarea,summary')]
                .filter(e=>{const a=e.getBoundingClientRect(),s=getComputedStyle(e);
                  return a.width>0 && a.height>0 && s.display!=='none' && s.visibility!=='hidden'
                         && (a.left < -1 || a.right > innerWidth+1)})
                .map(e=>e.tagName+':'+e.textContent.trim().slice(0,30));
              return {overflow:root.scrollWidth-root.clientWidth,clipped};
            }""")
            assert metrics["overflow"]<=1 and not metrics["clipped"], (engine,width,scale,metrics)
            # Overflow-hidden presentation is not a license to clip actual commands.
            for selector in (".syn-command-panel", ".syn-showcase", ".syn-showcase-visual"):
                region=page.locator(selector).first.evaluate("e=>({client:e.clientWidth,scroll:e.scrollWidth})")
                assert region["scroll"]<=region["client"]+1, (engine,width,scale,selector,region)
            assert not errors, (engine,"script errors",errors)
            if scale==1:
                if axe_file:
                    page.add_script_tag(path=str(axe_file))
                    result=page.evaluate("""async(tags)=>axe.run(document,{runOnly:{type:'tag',values:tags}})""",RULE_TAGS)
                    issues=[(v["id"],[n["target"] for n in v["nodes"]]) for v in result["violations"]]
                    assert not issues, (engine,width,"axe",issues)
                    print(engine,width,"axe 0 violations",len(result["incomplete"]),"incomplete checks",flush=True)
                if width==390:
                    page.keyboard.press("Tab")
                    assert page.evaluate("document.activeElement?.getAttribute('href')")=="#main", (engine,"skip link")
                    skip=page.locator(".premium-skip").bounding_box()
                    assert skip and skip["y"]>=0, (engine,"skip link placement",skip)
                    page.keyboard.press("Enter")
                    assert page.url.endswith("#main"), (engine,"skip link navigation",page.url)
                page.locator(".syn-command-row").first.focus()
                focus=page.locator(".syn-command-row").first.evaluate("""e=>{const s=getComputedStyle(e);
                    return {style:s.outlineStyle,width:parseFloat(s.outlineWidth),duration:s.transitionDuration}}""")
                assert focus["style"]!="none" and focus["width"]>=2, (engine,"focus",focus)
                assert focus["duration"].split(",")[0].strip()=="0s", (engine,"reduced motion",focus)
                page.get_by_role("searchbox",name="Find a destination").focus()
                assert page.evaluate("document.activeElement?.id")=="command-query"
                page.keyboard.press("Tab")
                assert page.evaluate("document.activeElement?.tagName")=="BUTTON", (engine,"keyboard order")
            cases+=1
        finally:
            context.close()
    context=browser.new_context(viewport={"width":390,"height":860},forced_colors="active",reduced_motion="reduce")
    try:
        page=context.new_page()
        page.goto(URL)
        page.locator(".syn-command-row").first.focus()
        state=page.locator(".syn-command-row").first.evaluate("""e=>({forced:matchMedia('(forced-colors:active)').matches,
           outline:getComputedStyle(e).outlineStyle,
           pixels:parseFloat(getComputedStyle(e).outlineWidth)})""")
        assert state["forced"] and state["outline"]!="none" and state["pixels"]>=2, (engine,"forced colors",state)
    finally:
        context.close()
    print("PASS",engine,cases,"viewports and forced colors",flush=True)

def main():
    cli=argparse.ArgumentParser()
    cli.add_argument("--browsers",nargs="+",default=["chromium","firefox","webkit"])
    cli.add_argument("--axe-file",type=Path)
    cli.add_argument("--webkit-executable",type=Path,help="optional locally provisioned WebKit launcher")
    args=cli.parse_args()
    if args.axe_file and not args.axe_file.is_file():cli.error("axe file not found")
    failures=0
    with sync_playwright() as pw:
        for engine in args.browsers:
            try:
                opts=chromium_launch_options() if engine=="chromium" else {"headless":True}
                if engine=="webkit" and args.webkit_executable:
                    opts["executable_path"]=str(args.webkit_executable)
                browser=getattr(pw,engine).launch(**opts)
            except Exception as e:
                failures+=1
                print("BLOCKED",engine,str(e)[:300],flush=True)
                continue
            try:
                audit(browser,engine,args.axe_file)
            except Exception as e:
                failures+=1
                print("FAIL",engine,repr(e),flush=True)
            finally:
                browser.close()
    return int(failures>0)

if __name__=="__main__":
    sys.exit(main())
