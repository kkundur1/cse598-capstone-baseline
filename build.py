"""Build PROPOSAL.docx: pandoc convert, then inject narrow page margins.

Pandoc regenerates word/document.xml from scratch, so page margins set in the
reference doc are discarded. They have to be patched into the output.
"""
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

here = Path(__file__).parent
docx = here / "PROPOSAL.docx"

subprocess.run(
    ["pandoc", "PROPOSAL.md", "-o", "PROPOSAL.docx",
     "--resource-path=.", "--reference-doc=reference-compact.docx"],
    cwd=here, check=True,
)

work = here / "_bw"
if work.exists():
    shutil.rmtree(work)
work.mkdir()
with zipfile.ZipFile(docx) as z:
    names = z.namelist()
    z.extractall(work)

dp = work / "word" / "document.xml"
d = dp.read_text(encoding="utf-8")

# 720 twentieths of a point = 0.5 inch
PGMAR = ('<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" '
         'w:header="360" w:footer="360" w:gutter="0"/>')

if "<w:pgMar" in d:
    d = re.sub(r"<w:pgMar[^>]*/>", PGMAR, d)
elif "<w:sectPr" in d:
    # insert as first child of sectPr
    d = re.sub(r"(<w:sectPr[^>]*>)", r"\1" + PGMAR, d, count=1)
else:
    # no sectPr at all: add one before </w:body>
    d = d.replace("</w:body>",
                  f'<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>{PGMAR}'
                  f"</w:sectPr></w:body>")

dp.write_text(d, encoding="utf-8")

tmp = here / "_out.docx"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    for n in names:
        p = work / n
        if p.is_file():
            z.write(p, n)
shutil.rmtree(work)
docx.unlink()
tmp.rename(docx)

check = zipfile.ZipFile(docx).read("word/document.xml").decode("utf-8")
print("pgMar present:", "<w:pgMar" in check)
