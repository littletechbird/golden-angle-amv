# Publish — littletechbird/golden-angle-amv

Exact commands to create and push this **public** documentation pack.

Docs, source code, captions, two small stills and the LICENSE only. Do **not** add video or audio.

---

## Prerequisites

- `gh` authenticated as a user that can create repos under **littletechbird**
- A working tree of this pack
- Public scrub already applied (no private names, private device names, private paths, cloud folder IDs, secrets, emails, phones or addresses)

---

## One-shot (init + create + push)

```bash
cd golden-angle-amv && \
git init -b main && \
git add . && \
git -c user.email='bot@littletechbird.local' -c user.name='Grok Bot' \
  commit -m 'The Golden Angle — public forever math music video craft pack' && \
gh repo create littletechbird/golden-angle-amv \
  --public \
  --source=. \
  --remote=origin \
  --push \
  --description 'The Golden Angle — 4K math music video craft pack (137.5° phyllotaxis formulas, render code, process, lessons; free forever)'
```

Expected remote after success:

**https://github.com/littletechbird/golden-angle-amv**

---

## Scrub check before push

```bash
git ls-files | grep -Ei '\.(mp4|mov|mkv|wav|mp3|png)$'   # expect nothing
du -sh assets                                              # small stills only
```

Then grep the tree for private names, local user paths, cloud-drive links, and anything that looks like a credential. Expect no hits.

Never commit credentials or API keys.

---

## Post-push checklist

- [ ] Repo is **public**
- [ ] README renders: thumbnail, Watch table, formula block, contact sheet, sister guides
- [ ] No video/audio in `git ls-files`
- [ ] Scrub grep clean
- [ ] Optional: add the X post URL to README + LINKS when it goes live
