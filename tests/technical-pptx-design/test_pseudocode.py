"""Tests for skills/technical-pptx-design/scripts/pseudocode.py: algorithms in an algorithm frame, as native tables.

Run from the repository root: python -m pytest tests (needs python-pptx, Pygments, pytest).
"""
import sys
from pathlib import Path

import pytest
from pptx.oxml.ns import qn
from pptx.util import Inches

sys.path.insert(0, str(Path(__file__).parents[2] / "skills" / "technical-pptx-design" / "scripts"))
from audit_pptx import audit, problem_count  # noqa: E402
from code_blocks import LIGHT  # noqa: E402
from pseudocode import add_pseudocode, parse, pieces  # noqa: E402
from pptx_helpers import new_widescreen_deck, remove_unused_layouts, set_theme_font  # noqa: E402

ALGORITHM = """Input: loads $q_t$
Output: peak $Q_{max}$
$Q_{max} \\gets 0$
for each hour $t$ do   // a pass over the year
    if $q_t > Q_{max}$ then
        $Q_{max} \\gets q_t$
    end if
end for
return $Q_{max}$
"""


def slide_of(deck):
    slide = deck.slides.add_slide(next(layout for layout in deck.slide_layouts if layout.name == "Title Only"))
    slide.shapes.title.text = "Algorithm"
    return slide


def text(table, row, column):
    return table.cell(row, column).text_frame.text.strip()


def has_line(cell, tag):
    return cell._tc.tcPr is not None and cell._tc.tcPr.find(qn(f"a:{tag}")) is not None


def test_parse_splits_header_depth_and_comments():
    headers, body = parse(ALGORITHM)
    assert headers == ["Input: loads $q_t$", "Output: peak $Q_{max}$"]
    assert [depth for depth, _, _ in body] == [0, 0, 1, 2, 1, 0, 0]
    assert body[1] == (0, "for each hour $t$ do", "a pass over the year")


def test_comment_marks_inside_maths_stay_in_the_code():
    _, body = parse("$a // b$ is the quotient ▷ integer division\n")
    assert body == [(0, "$a // b$ is the quotient", "integer division")]


def test_pieces_bold_keywords_and_italic_maths_with_scripts():
    assert pieces("for each $x_i^2$ do") == [("for", "bold"), (" ", ""), ("each", "bold"), (" ", ""), ("x", "italic"),
                                             ("i", "sub"), ("2", "sup"), (" ", ""), ("do", "bold")]
    assert pieces(r"$Q \gets \sum_z q$") == [("Q", "italic"), (" ← ∑", ""), ("z", "sub"), (" ", ""), ("q", "italic")]


def test_block_has_caption_header_numbers_guides_and_rules():
    deck = new_widescreen_deck()
    shape = add_pseudocode(slide_of(deck), ALGORITHM, Inches(0.6), Inches(1.6), Inches(8),
                           title="Algorithm 1: Peak load", marks={4: "yellow"})
    table = shape.table
    assert len(table.rows) == 1 + 2 + 7 and len(table.columns) == 1 + 2 + 1 + 1  # number, 2 indents, code, comment
    assert text(table, 0, 0) == "Algorithm 1: Peak load"
    assert text(table, 1, 0) == "" and text(table, 1, 1) == "Input: loads qt"
    assert [text(table, row, 0) for row in range(3, 10)] == [str(n) for n in range(1, 8)]
    assert text(table, 4, 4) == "▷ a pass over the year"
    # line 4, "if ... then" at depth 1: one guide on the first indent column, set on both cells of the edge
    assert has_line(table.cell(5, 1), "lnL") and has_line(table.cell(5, 0), "lnR")
    assert not has_line(table.cell(4, 1), "lnL")  # "for", at depth 0, has none
    assert has_line(table.cell(0, 3), "lnT") and has_line(table.cell(0, 3), "lnB") and has_line(table.cell(1, 3), "lnT")
    assert has_line(table.cell(9, 0), "lnB")
    assert str(table.cell(6, 0).fill.fore_color.rgb) == LIGHT["yellow"]
    runs = [r for row in table.rows for cell in row.cells for p in cell.text_frame.paragraphs for r in p.runs]
    assert {r.font.name for r in runs} == {None}  # the deck's own font
    assert any(r.font.bold and r.text == "return" for r in runs)


def test_pseudocode_refuses_the_diff_colours():
    deck = new_widescreen_deck()
    with pytest.raises(ValueError):
        add_pseudocode(slide_of(deck), ALGORITHM, Inches(0.6), Inches(1.6), Inches(8), marks={1: "red"})


def test_audit_accepts_pseudocode_without_a_code_font(tmp_path):
    deck = new_widescreen_deck()
    add_pseudocode(slide_of(deck), ALGORITHM, Inches(0.6), Inches(1.6), Inches(8), title="Algorithm 1: Peak load")
    set_theme_font(deck, "Calibri")
    remove_unused_layouts(deck)
    deck.save(tmp_path / "deck.pptx")
    assert problem_count(audit(tmp_path / "deck.pptx")) == 0
