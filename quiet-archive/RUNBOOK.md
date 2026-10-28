# The Quiet Archive — production runbook

Channel: The Quiet Archive (YouTube channel id `UCnsOidpUHcQgwUKl_bcxwng`, handle @thequietarchivetales).
Niche: true historical mysteries and disappearances, English, US/UK/CA/AU audience, faceless, AI narration.
Owner instructions: Claude runs the channel end to end, free tools only, and only notifies the owner when needed
(login/verification needed, copyright or policy warning, a video far above/below average, Tier 1/Tier 2 reached,
or an irreversible decision such as deleting a video or renaming the channel).

## Owner rules (2026-10-29)
1. **Every upload discloses AI**: in Studio set "Altered or synthetic content" (Sử dụng AI) = **Yes / Có** on every video and
   Short, and keep the AI-narration line in every description.
2. **Every video is one complete, standalone story** with its own title and name. No episode numbers, no series framing,
   no "part 1/part 2", no references to other videos inside the narration.
3. **Daily output: at least 1 long-form and at least 2 Shorts per day.**

## Cadence (times US Eastern, the audience's clock; Studio is set to GMT+7)
- Long-form, one per day, best slot per weekday (Buffer 1.8M-video study, SocialPilot 301K study):
  Mon 9:00 AM · Tue 9:00 AM · Wed 2:00 PM · Thu 5:00 PM · Fri 12:00 PM · Sat 12:00 PM · Sun 10:00 AM ET.
- Shorts, two per day: 6:00 PM and 9:00 PM ET (Shorts engagement peaks 6–11 PM). Cut from that day's or a recent
  long-form, or a standalone mini-story; each Short is complete in itself and has its own title.
- ET→GMT+7: add 12 h in EST (Nov–Mar), 11 h in EDT (Mar–Nov).
- Production: a daily run (~13:00 Asia/Saigon) makes tomorrow's long-form + 2 Shorts and schedules them. Keep a 1-day buffer.
- Trade-off noted to owner: Shorts at 67% of uploads is above the ~55% level where long-form tends to weaken; watch
  long-form watch time weekly and tell the owner if it drops.
- From ~30 days of data, move slots to the channel's own "When your viewers are on YouTube" report.

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
    not made for kids, no paid promotion, AI use ("Sử dụng AI") = **Yes**,
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
