# The Quiet Archive — production runbook

Channel: The Quiet Archive (YouTube channel id `UCnsOidpUHcQgwUKl_bcxwng`, handle @thequietarchivetales).
Niche: true historical mysteries and disappearances, English, US/UK/CA/AU audience, faceless, AI narration.
Owner instructions: Claude runs the channel end to end, free tools only, and only notifies the owner when needed
(login/verification needed, copyright or policy warning, a video far above/below average, Tier 1/Tier 2 reached,
or an irreversible decision such as deleting a video or renaming the channel).

## Cadence (researched 2026-10-28; times are US Eastern, the audience's clock)
- Long-form 15–20 min: **Wednesday 2:00 PM ET** and **Sunday 10:00 AM ET**.
  - In Studio (time zone GMT+7): while US is on EDT (Mar–Oct) Wed 14:00 ET = **Thu 01:00**, Sun 10:00 ET = **Sun 21:00**;
    while US is on EST (Nov–Mar) Wed 14:00 ET = **Thu 02:00**, Sun 10:00 ET = **Sun 22:00**.
  - Why: Buffer (≈1.8M videos, Jul 2026) ranks Sunday 9–10 AM the top long-form slot; SocialPilot (301K videos, 2026)
    ranks Wed–Fri 2–4 PM and Sunday 8–10 AM highest; education content does best Tue–Wed early afternoon.
- One Short per week: **Friday 5:00 PM ET** (Sat 04:00 EDT / 05:00 EST in GMT+7), cut from the latest long-form,
  linked via Related Video. Shorts ≤ 40% of uploads.
- Under ~1,000 subscribers timing matters little; never hold a finished episode back for more than a few days.
- From ~30 days of data, switch to the channel's own "When your viewers are on YouTube" report and move slots
  1–2 hours before its peak.
- Keep at least one finished episode scheduled ahead.

## One episode, step by step
1. Pick the next unused topic from `topics.md`; check it is not in `published.md`. Mark it in progress.
2. Research with WebSearch/WebFetch; open the pages you cite. Minimum 3 independent sources.
3. Write `epNN/script.md` (2,200–2,900 words) in the scene format of `ep01/script.md`
   (`## sNN | visual_key | caption`). Hook in the first 30 s, chapters every 1–2 min,
   end with a "Documented vs legend" section and a question for the comments.
   Leave the **last 20 s** as an outro (subscribe line over a quiet visual) so the end screen fits.
4. Add any new visual keys to `pipeline/visuals.py` (procedural art only; no stock photos,
   no photos of real people, no copyrighted art). Render frames, look at a contact sheet, fix overlaps.
5. Narration (v2): Kokoro-82M ONNX (`kokoro-v1.0.onnx` + `voices-v1.0.bin` from GitHub release
   thewh1teagle/kokoro-onnx model-files-v1.0; vocab from that repo's config.json; phonemes from the espeak-ng
   binary inside the Piper release) → `pipeline/narrate2.py epNN/script.md epNN/audio af_heart 0.95`.
6. Video (v2): one module `scenes_epNNb.py` with VARIANTS (2–3 images per visual), FRAMES and FX;
   stills to `epNN/frames/sNN_k.png`; then `pipeline/render2.py epNN scenes_epNNb --parallel 2 --mood sea`.
   Smooth float camera, 7.5 s shots, crossfades, rain/fog/dust/flicker, lower-third captions, [[TEXT]] kinetic titles,
   voice chain + synthesized ambient bed with ducking, -14 LUFS. Files > 95 MB: split for GitHub and re-join in the
   browser (`new Blob([part0, part1, ...])`).
   Each video is a standalone story: no episode numbers, no series framing, no "previous episode" references.
7. Thumbnail 1280×720: max 4 words, one silhouette subject, amber label. Make 2–3 variants for Studio's A/B test.
8. Push `epNN/video.mp4`, `thumbnail*.jpg`, `captions-en.srt` to this repo under `quiet-archive/epNN/`.
9. Upload in YouTube Studio using the Claude desktop app's built-in browser:
   in the upload dialog, `fetch()` the raw.githubusercontent.com file, wrap it in a `File`,
   assign it to the dialog's `input[type=file]` via `DataTransfer`, dispatch `change`.
   Same trick for the thumbnail (`input#file-loader`) and the captions file
   (Subtitles → Upload file → "with timing", then set the hidden file input).
10. Details: title, description (summary, CHAPTERS, DOCUMENTED vs LEGEND, SOURCES, AI-narration note, 3 hashtags),
    not made for kids, no paid promotion, AI-altered content = **No** (illustrations are not realistic),
    tags, language English (United States), category Education, add to the matching playlist.
11. Elements: English captions; end screen = subscribe + best-for-viewer video over the last 20 s.
12. Visibility: Schedule (not Premiere) at the next slot; convert ET to GMT+7 as in Cadence.
13. Append to `published.md`: date, slot, title, video id, topic.
14. After 48 h and 7 days: record CTR, average view duration and views in `published.md`;
    every 5 episodes compare and shift topics toward what wins.

## Account status (check every run)
- Phone verification (youtube.com/verify) is required for: custom thumbnails and A/B tests, videos longer than 15 min,
  clickable links in descriptions, and linking a Short to a related video. Only the owner can do it (phone + SMS code).
- Until it is done: keep long-form at 14:30 max, pick the best of the 3 auto frames as thumbnail, and re-apply the custom
  thumbnails (`epNN/thumbnail*.jpg`) and related-video links as soon as verification is detected.
- Test for verification: on a video's edit page, set the custom thumbnail file input; if "Save" stays disabled the
  channel is not verified yet.

## Policy guard rails
- No re-uploaded or third-party footage; every visual is generated here.
- No real living victims; nothing presented as fact that is legend; no misleading titles.
- Do not mass-produce: each script is researched and edited individually; vary structure between episodes.
