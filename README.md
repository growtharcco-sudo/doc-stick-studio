# Doc Stick studio

Weird facts about your body, explained by a deadpan stick-figure doctor. The stuff school skipped.

```
briefs/<id>.json  --pipeline/kit.py-->  specs/<id>.json  --pipeline/make_reel.py-->  queue/<id>/video.mp4
```

- `pipeline/kit.py`: brief -> spec with named slots + layout check (exits 1 on LAYOUT PROBLEMS)
- `pipeline/make_reel.py`: channel rule checks, voice, render. `--sheet` = one check image for the whole Reel
- `pipeline/engine.py`: frames, captions, lip sync, sound effects, cover
- `pipeline/chars.py`: Doc Stick, the boy and the girl. `pipeline/props.py`: every prop (add new ones here)
- `pipeline/voice.py`: Kokoro am_michael narration (model downloads once to ~/.cache/kokoro)
- `assets/fonts`: Inter Display Black (SIL Open Font License)

- `poster/`: posting (GitHub Actions): `publish_due.py` posts queued Reels at `post_at` to YouTube and Instagram;
  videos are served from the `media` branch by GitHub Pages
- `tools/`: `check_keys.py`, `deep_check.py` (no public posts), `get_youtube_token.py`
- `pages/`: the public site (home, privacy, terms) shown on GitHub Pages

How to make a Reel: `ROUTINE.md`. One-time setup: `SETUP.md`.
