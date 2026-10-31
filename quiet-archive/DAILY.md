# Daily production run — The Quiet Archive

Goal of each run: keep the schedule filled at least 2 days ahead with **2 long-form + 2 Shorts per day**, all in the
Archie (v3) style, and review analytics. Owner gave full authority (2026-10-29) except: never handle passwords/OTP/ID
verification, never publish immediately (schedule only), never delete videos (owner deletes), never change residence
country without asking.

## 0. Setup (fresh session)
```
git clone https://github.com/phanconghuyhoang/phanconghuyhoang.git /home/claude/phanconghuyhoang
cd /home/claude/phanconghuyhoang/quiet-archive && ./setup.sh
```
Commit as `Claude <noreply@anthropic.com>`; end messages with the attribution lines the session gives.

## 1. FIRST: check what is already scheduled (owner rule 2026-10-31 — never produce for slots that are full)
Open Studio > Nội dung (Video tab AND Shorts tab), read every "Đã lên lịch" row (date + time on the row's hover/edit),
and reconcile with `published.md`. Build the slot table below for the next 4 days and produce ONLY for the first
empty slots. **Never schedule more than 5 days after today's date (owner rule 2026-10-31)** — e.g. on 31 Oct
the last allowed date is 5 Nov. If everything is filled ≥2 days ahead, do analytics + improvements instead of new videos.

Daily slots (owner rule 2026-10-31: **2 long-form + 2 Shorts per day, fixed times**). Studio is GMT+7:
| Slot | ET | VN (EST, 2 Nov 2026 – 8 Mar 2027) | VN (EDT, from 8 Mar 2027) |
|---|---|---|---|
| Long A | 15:00 | 03:00 | 02:00 |
| Long B | 09:00 | 21:00 (same date) | 20:00 |
| Short 1 | 18:00 | 06:00 | 05:00 |
| Short 2 | 21:00 | 09:00 | 08:00 |
Why these (research 2026-10-31, SocialPilot 301K videos + OpusClip Shorts data): US long-form performs best
weekday 2–4 PM and weekend 8–10 AM local → Long A 3 PM ET, Long B 9 AM ET. Shorts peak in the evening (6–9 PM ET)
→ 18:00 / 21:00 ET. Small channels (<1K subs) gain most from consistency, so the times stay fixed. After ~28 days,
re-check Studio > Đối tượng > "Khi người xem của bạn có mặt trên YouTube" and shift if the heatmap disagrees.
Saturday extra deep-dive is replaced by Long B (each day has 2 long-forms now).

## 2. Analytics (every run, before producing)
Studio > Analytics (built-in browser). For each public video ≥24 h old fill `analytics.md` (views, impressions, CTR,
AVD, retention drop, traffic source, subs; Shorts: viewed vs swiped). Add a channel snapshot row. Decide:
- CTR < 4% after 1,000 impressions → new thumbnail/title (A/B test via "Thử nghiệm A/B").
- First-30 s retention < 65% → stronger cold open next time.
- Double down on topics/formats that beat the channel average. Note the decision in the Action column.

### 2b. Every-5-days deep review (owner rule 2026-10-31): 5 Nov, 10 Nov, 15 Nov, 20 Nov … (first run of that day)
Daily runs only RECORD numbers; direction changes happen in this review. Write a section "Review DD/MM" in analytics.md
and send the owner a short Vietnamese summary.
1. Own channel, last 5 days vs previous 5: views, watch hours, subs, CTR, AVD, retention, traffic sources; rank every
   long-form and Short; A/B results; Short → long-form click-through; progress to monetization (1K subs + 4K h, or 10M
   Shorts views/90 d).
2. Competitors (5–8 channels on the same niche, big + small fast-growing; keep the list in analytics.md): their uploads
   in the last 5 days, which beat their own average, topic, length, title/thumbnail style, posting time, cold open,
   how their Shorts push to long-forms.
3. Trends: searches/news/films/games/memes that can hook into a history story.
4. Compare + conclude: where we are weaker, which topics/formats win, gaps nobody covers.
5. Adjust for the next 5 days — at most 3 changes so their effect is measurable (topic list, default thumbnail/title
   style, cold open + joke rhythm, length, slots). Log: change, metric, check next review.
Big changes (niche, mascot, daily volume) = proposals only; the owner decides.

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
- Shorts 35–55 s, vertical, standalone mini-story, hook text in first second. END with a bridge to the long-form
  ("The full story is on the channel — link above"), not just "Follow". Description first line:
  "Watch the full story: <long title> <youtu.be link>". When the long-form is public, set "Video có liên quan"
  (edit page, `#linked-video-editor-link`, pick the card, Save). Check this every run for Shorts whose long went public.
- Trends (owner 2026-10-31): every script gets 1–2 hooks to what is trending now (news, a game/film/meme, an
  anniversary) — search before writing; put one in the cold open. Comedy: punchline every 2–3 lines in the first
  60 s, an open loop ("…and that's not even the weird part") every 1–2 minutes to hold retention.

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
3. Thumbnail: `input#file-loader`. "Hiện thêm" (`#toggle-button`): radio **"Có, đã dùng AI" — always**, and radio **"Không, video của tôi không chứa nội dung được trả tiền để quảng cáo" — always** (owner 2026-10-31; it is NOT preselected). Tags: focus
   `#tags-container input`, type with commas, press Return.
4. Next → `#subtitles-button` → "Tải tệp lên" → "Có thông tin thời gian" → set `#captions-file-loader` → "Xong".
5. Next twice → "Lên lịch" → `#datepicker-trigger`, focus date input, ctrl+a, type `DD thg MM, YYYY`, Return; time:
   click `#time-of-day-container input`, click `tp-yt-paper-item` "HH:MM". Then `#done-button`; read the confirmation.
6. Description = story summary, chapters (long-form), Documented vs Legend, sources, the footer:
   "The Quiet Archive: … New stories every day. Subscribe: https://www.youtube.com/@thequietarchivetales?sub_confirmation=1"
   and "AI disclosure: the narration is AI-generated (text-to-speech) and the illustrations are computer-generated
   original artwork. The script was researched from the sources above and reviewed before upload." + 3 hashtags.
7. Long-form: on the video's edit page open "Thử nghiệm A/B" → "Tiêu đề và hình thu nhỏ": 3 pairs, each a DIFFERENT
   thumb4.py style (reaction / cinematic / evidence / question) and a different title angle (searchable name /
   shocking fact / myth-busting question). Log variants in analytics.md; pick defaults from the winners.
8. Shorts: when the long-form of the same case is public, add it as "Video có liên quan".

## 7. After publishing days
- Public videos: end screen (subscribe + best related video), add to pillar playlists, pin a question comment.
- NO compilations or re-cuts of earlier videos (owner rule, 2026-10-29). For watch hours, make one longer standalone
  deep-dive (18–25 min, one complete story) per week instead.

## 8. Log and report
Append to `published.md` (id, title, slot), update `analytics.md`, commit and push. Send the owner a short Vietnamese
summary with SendUserMessage: what was scheduled, key numbers, decisions, anything that needs them.
