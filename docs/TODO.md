# TODO

Ideas for later. Nothing here is planned or built yet.

## More games

Use other games besides Galaga. The action also offers Pac-Man, Breakout, Tetris and Snake, among others. Each one must be checked with `merge_svg.py`, which has only been tested with Galaga.

An image in a README cannot run code, so it cannot choose a random game on each page reload. Options:

- A different game each day, chosen when the image is regenerated.
- A different game per coin, for everyone.
- A real random game per reload, which needs an external service that serves the image. It would add infrastructure to maintain, and GitHub caches images anyway, so it may not change on every reload.

## More festive events

Add more themes to `scripts/seasons.py`. Candidates:

- Tamborrada in Donostia (20 January).
- Carnival.
- Halloween.

Dates that change each year need a fixed window, like Zinemaldia, or a table to update.
