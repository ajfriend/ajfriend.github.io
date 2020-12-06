# Pandoc/Markdown/LaTeX

- `brew install pandoc`
- `brew install --cask mactex` 

The latest version of `pandoc` actually translates
math to Word `.docx` files pretty well.

$$
\sum_{i=1}^n (x + 1)^i
$$

Use `pandoc pandoc.md -o test.docx` for Word
or `pandoc pandoc.md -o test.pdf` for PDF.

## References

- [TUG 2020 — John MacFarlane — Pandoc for TeXnicians](https://www.youtube.com/watch?v=T9uZJFO54iM)
- Tikz
    + https://www.overleaf.com/learn/latex/TikZ_package#Diagrams
    + <https://www.overleaf.com/learn/latex/LaTeX_Graphics_using_TikZ:_A_Tutorial_for_Beginners_(Part_1)%E2%80%94Basic_Drawing>
    + http://cremeronline.com/LaTeX/minimaltikz.pdf
    + https://tex.stackexchange.com/questions/61429/how-to-draw-a-hexagonal-grid-with-numbers-in-the-cells
    + https://tikzit.github.io/
