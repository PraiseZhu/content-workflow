# article-image-styles

Style packs for `../article-image-template`. One folder per pack; `ACTIVE` holds the default pack name
(an article's `article.yaml` `style:` overrides it). A renderable pack has `style.json` (palette, fonts, frame grid)
and `tokens.css` (CSS %-template). Packs are add-only: for a big change copy to `<name>-v2`.

| pack | renderable | notes |
|---|---|---|
| dark-grid-photo | yes | deep green-black, tinted photo, white grid, orange accent, grain. refs/ |
| house-dark | no (pointer) | lives at ../house-dark (own HTML/Python generators); not yet ported to this template |

Candidate styles collected elsewhere become packs here once chosen.
