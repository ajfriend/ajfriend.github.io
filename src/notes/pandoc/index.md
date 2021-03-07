# Pandoc/Markdown/LaTeX

- `brew install pandoc`
- `brew install --cask mactex`


## Markdown to Google Docs or Word

The latest version of `pandoc` actually translates
math to Word `.docx` files pretty well.

$$
\sum_{i=1}^n (x + 1)^i
$$

Use `pandoc pandoc.md -o test.docx` for Word
or `pandoc pandoc.md -o test.pdf` for PDF.


### Reference files

You can change the output style when writing
to Microsoft Word (which you then might convert to Google Docs)
by setting a custom `reference.docx` with the `--reference-doc` 
option.

See the notes on `--reference-doc` under the 
["Options affecting specific writers" section](https://pandoc.org/MANUAL.html#options-affecting-specific-writers)
of the pandoc documentation.

You would convert your markdown with a command like

```sh
pandoc test.md -o test.docx --reference-doc=aj-reference.docx -f markdown-auto_identifiers
```

The `-f markdown-auto_identifiers` is to remove weird bookmarks
at the start of each section. See https://pandoc.org/MANUAL.html#headings-and-sections.

The `reference-doc` must be
[created with Microsoft Word](https://support.microsoft.com/en-us/office/customize-styles-in-word-for-mac-1ef7d8e1-1506-4b21-9e81-adc5f698f86a?ui=en-us&rs=en-us&ad=us)---Google Docs wont' work.
Fonts won't translate exactly between Word and Docs, so you may have to play with those a bit.

Here are two `reference-doc` examples I've created:

- [`aj-reference-black.docx`](aj-reference-black.docx)
- [`aj-reference-blue.docx`](aj-reference-blue.docx)

### Example

Here's an example created with

```sh
pandoc test.md -o test.docx --reference-doc=aj-reference-blue.docx -f markdown-auto_identifiers
```

https://gist.github.com/ajfriend/b7614596acb479850e55b722490d756d


### TODO

- bulleted lists don't turn out great; have to figure out how to fix the spacing

## References

- [TUG 2020 — John MacFarlane — Pandoc for TeXnicians](https://www.youtube.com/watch?v=T9uZJFO54iM)
- Tikz
    + https://www.overleaf.com/learn/latex/TikZ_package#Diagrams
    + <https://www.overleaf.com/learn/latex/LaTeX_Graphics_using_TikZ:_A_Tutorial_for_Beginners_(Part_1)%E2%80%94Basic_Drawing>
    + http://cremeronline.com/LaTeX/minimaltikz.pdf
    + https://tex.stackexchange.com/questions/61429/how-to-draw-a-hexagonal-grid-with-numbers-in-the-cells
    + https://tikzit.github.io/
