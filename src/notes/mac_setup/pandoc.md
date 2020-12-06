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
