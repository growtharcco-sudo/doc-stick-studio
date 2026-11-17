# Doc Stick studio

This repo makes and posts two Reels a day for Doc Stick (Instagram and YouTube @askdocstick).
For every run, follow `ROUTINE.md` step by step. Never post directly: queue it, and GitHub Actions posts at `post_at`.
Hard rules:
- Write a brief and build the spec with `pipeline/kit.py`. Never hand-write coordinates or edit specs by hand.
- Check a Reel with `make_reel.py --sheet` and read only that one sheet.png, not single stills.
- Every fact from a reputable source fetched the same day; every number in `math`, checked in Python.
- Health safety: facts about how the body works only. No doses, no treatment instructions, no diagnosis;
  "see a doctor if..." for symptoms. Nothing sexual or suggestive on screen (intercourse only implied, never shown).
- No em dashes or en dashes. Instagram caption ends with a real question, then exactly 5 hashtags including
  #docstick. YouTube description says "Educational only, not medical advice.", has a Sources list and 3 hashtags including #Shorts.
- Voice is Kokoro am_michael, speed 1.0, clean. Instagram AI label and YouTube synthetic-content disclosure stay on.
- Full quality: 1080x1920, 30 fps, CRF 16. Never lower quality to save time or file size.
- Do not change Doc Stick, the boy, the girl or the look (chars.py, engine.py drawing) unless Samrit asks.
  New props for new topics are fine (pipeline/props.py, same style).
- If Samrit replies "skip", create `queue/<id>/SKIP`, commit and push.
- Never put tokens or passwords in files or chat: they live only in GitHub Secrets.
