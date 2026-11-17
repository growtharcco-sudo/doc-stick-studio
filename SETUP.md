# One-time setup

Everything is free. Keys go only into GitHub's encrypted Secrets, never into a file or a chat.
Claude guides each step one screen at a time.

## A. GitHub
1. Repo `growtharcco-sudo/doc-stick-studio`, Public (done), Claude GitHub app has access (done).
2. Repo -> Settings -> Pages -> Source *Deploy from a branch* -> `media` / `(root)` -> Save.
   Check: https://growtharcco-sudo.github.io/doc-stick-studio/ shows the channel page.

## B. Instagram key (never expires): reuse the Meta system user and app
Trap: switching Instagram to a professional account can silently create a NEW business portfolio. The account must
end up in the **The Real Number** portfolio, linked to a new Facebook Page "Doc Stick" there.
1. @askdocstick is a Professional (Creator or Business) account linked to the Facebook Page "Doc Stick".
2. business.facebook.com -> portfolio **The Real Number** -> Accounts: add the Doc Stick Page and @askdocstick as assets.
3. Settings -> Users -> System users -> **unhyped-poster** -> Assign assets: the Doc Stick Page and @askdocstick, Full control.
   Trap: check it really shows Full access on BOTH (it can say "Nothing assigned yet").
4. Generate new token -> app **Real Number Studio** -> expiration **Never** -> permissions `instagram_basic`,
   `instagram_content_publish`, `pages_show_list`, `pages_read_engagement` -> that is `IG_TOKEN` (starts with EAA).
5. `IG_USER_ID`: leave it out at first and run **Actions -> Check keys**: it prints the ID to use.

## C. YouTube key: a NEW Google Cloud project for Doc Stick (its own daily upload quota)
1. console.cloud.google.com -> New project "Doc Stick Studio" -> enable **YouTube Data API v3**.
2. Google Auth Platform -> Branding: app name "Doc Stick Studio", home page https://growtharcco-sudo.github.io/doc-stick-studio/,
   privacy .../privacy.html, terms .../terms.html, authorized domain `growtharcco-sudo.github.io`.
   Trap: "Publish app" stays greyed out until these links and the domain are in.
3. Data access: scopes `.../auth/youtube.upload` and `.../auth/youtube`. Audience: External -> **Publish app** (In production).
4. Clients -> Create client -> **Desktop app** -> download the JSON.
   Trap: redirect_uri_mismatch = wrong client type (must be Desktop) or an older client_secret file in Downloads.
5. On a laptop: `pip3 install google-auth-oauthlib`, then
   `python3 tools/get_youtube_token.py ~/Downloads/client_secret_XXXX.json` (the NEWEST file). At sign-in choose the
   **Doc Stick** channel (@askdocstick). It prints `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
   Uploads go PUBLIC directly, with the "altered or synthetic content" disclosure on.

## D. Secrets
Repo -> Settings -> Secrets and variables -> Actions -> New repository secret, one each:
`IG_TOKEN`, `IG_USER_ID`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
Paste only the value (if a label or spaces slip in, the code cleans them).

## E. Test (posts nothing publicly)
1. **Check keys** (Claude runs it by pushing to `checks/`): prints the Instagram username, YouTube channel name and IDs.
2. **Deep check** (Claude runs it by pushing `checks/deep.txt`): Instagram processes a test Reel without publishing it;
   YouTube gets an UNLISTED test upload that is checked (stays unlisted = public uploads work), given the thumbnail, then deleted.
3. One real end-to-end post, then the daily task is switched on.

## F. Scheduled task (Claude)
ONE cloud task, "Doc Stick daily", runs `ROUTINE.md` section A every day at about 2:30 PM IST.
It needs "Skip all approvals" (Automatically approve) on and no connectors it doesn't use.
