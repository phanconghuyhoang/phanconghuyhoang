# Daily production run — The Quiet Archive

Goal of each run: keep the schedule filled at least 2 days ahead with **1 long-form + 2 Shorts per day**, all in the
Archie (v3) style, and review analytics. Owner gave full authority (2026-10-29) except: never handle passwords/OTP/ID
verification, never publish immediately (schedule only), never delete videos (owner deletes), never change residence
country without asking.

## 0. Setup (fresh session)
```
git clone https://github.com/phanconghuyhoang/phanconghuyhoang.git /home/claude/phanconghuyhoang
cd /home/claude/phanconghuyhoang/quiet-archive && ./setup.sh
```
Commit as `Claude <noreply@anthropic.com>`; end messages with the attribution lines the session gives.

## 1. What is already scheduled
Read `published.md` (log of every upload and slot). Fixed slots (YouTube Studio is GMT+7):
- Long-form 15:00 ET → **03:00 VN** (EST, from 2 Nov 2026; until 8 Mar 2027). Shorts 18:00/21:00 ET → **06:00 / 09:00 VN**.
- Saturdays (owner-approved 2026-10-29): one EXTRA long-form deep-dive, 18–25 min, a NEW standalone story (never a
  compilation), at 12:00 ET Saturday = 00:00 VN Sunday (EST; 23:00 VN Saturday during EDT). First one: Sat 31 Oct 12:00 EDT = Sun 1 Nov 00:00? No — 31 Oct is EDT → 23:00 VN Sat 31 Oct; from 7 Nov use 00:00 VN Sunday.
- Review ~15 Nov 2026: if CTR and retention are stable, add a second daily long-form at 09:00 ET (21:00 VN), on winning topics.
- From 8 Mar 2027 (EDT) shift all to 02:00 / 05:00 / 08:00 VN.
Find the first VN date whose 3 slots are not all filled; produce for that date (and the next if time allows).

## 2. Analytics (every run, before producing)
Studio > Analytics (built-in browser). For each public video ≥24 h old fill `analytics.md` (views, impressions, CTR,
AVD, retention drop, traffic source, subs; Shorts: viewed vs swiped). Add a channel snapshot row. Decide:
- CTR < 4% after 1,000 impressions → new thumbnail/title (A/B test via "Thử nghiệm A/B").
- First-30 s retention < 65% → stronger cold open next time.
- Double down on topics/formats that beat the channel average. Note the decision in the Action column.

## 3. Pick topics
`topics.md` = backlog. Prefer US-searchable cases (Roanoke, Amelia Earhart, USS Cyclops, Dyatlov Pass, Bermuda
Triangle cases, Lost Colony, Flight 19, Oak Island, Franklin expedition, Dancing Plague, Tunguska, etc.). Each video is
a complete standalone story: no parts, no episode numbers, no references to other videos. Check facts with WebSearch /
WebFetch (Wikipedia + 1–2 more sources) and list them in the description. Avoid cases with living victims/relatives
being hurt, graphic violence, and political conspiracy. Search briefly for what big channels titled the same case and
for current trends (anniversaries, news like wreck discoveries).

## 4. Write (v3 format — see pipeline/narrate3.py docstring)
- Long-form 9–14 min (≈1,400–2,000 words): cold open on the strangest fact → Archie intro in `room` → story on
  stages with cast → myths vs record → theories (comic but fair) → "Documented vs Legend" → comment question + subscribe.
- Voice: Archie, dry witty American humour, a punchline every few lines, jokes on myths/officials/bad luck — never on
  victims. Tags: {a:pose/expr} {c:...} {t:BIG TEXT} {s:sfx} {p:sec} {z} {cam:...} {bg:...}.
- Poses: idle talk point_r point_l point_up shrug facepalm scared think lean_in arms_wide jump hands_hips wave sit
  walk_a lie. Expressions: neutral smug shocked scared deadpan laugh sad suspicious angry wink.
- Cast looks: captain sailor keeper redhair official beard woman judge writer archie. Feet y ≈ floor (0.80–0.88).
- SFX: whoosh pop boing thud ding sting tick scratch crickets.
- Backdrops: reuse `mc/bg/*.png`, `ep01/frames`, `ep02/frames`, or add new ones to `pipeline/backdrops.py` (flat cartoon,
  2560x1440, clear floor line). New topic → usually 4–8 new backdrops.
- Shorts 35–55 s, vertical, standalone mini-story, hook text in first second, end with "Follow for…".

## 5. Produce
```
python3 pipeline/narrate3.py <dir>/script.md <dir>/audio am_michael 1.0
python3 pipeline/render3.py <dir> --parallel 2 --mood sea|dread        # long-form
python3 pipeline/render3.py <dir> --vertical --mood sea|dread          # Short
python3 pipeline/thumb3.py <bg.png> <dir>/thumbnail.jpg "3-4 WORDS" point_l shocked   # + thumb_b, thumb_c
```
Check frames (ffmpeg -ss … -frames:v 1) before uploading. Captions = `<dir>/audio/narration.srt`.
Run long jobs with run_in_background (not nohup).

## 6. Upload (built-in browser, Studio tab)
Push the files first (split > 95 MB: `split -b 90m -d final.mp4 final.mp4.part`). In the page:
1. `navigate https://www.youtube.com/upload`; fetch raw.githubusercontent parts in the page, keep the File on
   `window.__f`, then set it on `input[type=file]` via DataTransfer + `change` event (fetch in a background promise and poll — 90 MB ≈ 60 s).
2. Click once on the dialog heading (real click, gives the page focus). Set title/description with a Range selection
   on each `ytcp-uploads-dialog #textbox` + `document.execCommand('insertText')`.
3. Thumbnail: `input#file-loader`. "Hiện thêm" (`#toggle-button`): radio **"Có, đã dùng AI" — always**. Tags: focus
   `#tags-container input`, type with commas, press Return.
4. Next → `#subtitles-button` → "Tải tệp lên" → "Có thông tin thời gian" → set `#captions-file-loader` → "Xong".
5. Next twice → "Lên lịch" → `#datepicker-trigger`, focus date input, ctrl+a, type `DD thg MM, YYYY`, Return; time:
   click `#time-of-day-container input`, click `tp-yt-paper-item` "HH:MM". Then `#done-button`; read the confirmation.
6. Description = story summary, chapters (long-form), Documented vs Legend, sources, the footer:
   "The Quiet Archive: … New stories every day. Subscribe: https://www.youtube.com/@thequietarchivetales?sub_confirmation=1"
   and "AI disclosure: the narration is AI-generated (text-to-speech) and the illustrations are computer-generated
   original artwork. The script was researched from the sources above and reviewed before upload." + 3 hashtags.
7. Long-form: start "Thử nghiệm A/B" with thumbnail, thumb_b, thumb_c when the editor offers it.
8. Shorts: when the long-form of the same case is public, add it as "Video có liên quan".

## 7. After publishing days
- Public videos: end screen (subscribe + best related video), add to pillar playlists, pin a question comment.
- NO compilations or re-cuts of earlier videos (owner rule, 2026-10-29). For watch hours, make one longer standalone
  deep-dive (18–25 min, one complete story) per week instead.

## 8. Log and report
Append to `published.md` (id, title, slot), update `analytics.md`, commit and push. Send the owner a short Vietnamese
summary with SendUserMessage: what was scheduled, key numbers, decisions, anything that needs them.
