"""Assemble scene stills + narration into a 1080p video.

usage: render.py <ep_dir>   (expects <ep_dir>/frames/sNN.png and <ep_dir>/audio/scenes.json)
"""
import json, os, subprocess, sys

FPS = 25
FADE = 0.5


def run(cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def main(ep):
    scenes = json.load(open(os.path.join(ep, "audio", "scenes.json")))
    clips_dir = os.path.join(ep, "clips"); os.makedirs(clips_dir, exist_ok=True)
    lst = []
    for i, sc in enumerate(scenes):
        d = sc["duration"]
        n = int(d * FPS) + 1
        img = os.path.join(ep, "frames", sc["id"] + ".png")
        wav = os.path.join(ep, "audio", sc["audio"])
        out = os.path.join(clips_dir, sc["id"] + ".mp4")
        # alternate push-in / pull-out with a slight drift; scale up first so zoompan stays smooth
        if i % 2 == 0:
            z = f"min(1+0.05*on/{n},1.05)"
        else:
            z = f"max(1.05-0.05*on/{n},1.0)"
        x = "iw/2-(iw/zoom/2)" if i % 3 else f"(iw-iw/zoom)*on/{n}"
        vf = (f"scale=2880:1620,zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={n}:s=1920x1080:fps={FPS},"
              f"fade=t=in:st=0:d={FADE},fade=t=out:st={max(d - FADE, 0):.3f}:d={FADE},format=yuv420p")
        run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img, "-i", wav,
             "-vf", vf, "-t", f"{d:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "28", "-x264-params", "keyint=750",
             "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "2", out])
        lst.append(f"file '{os.path.abspath(out)}'")
        print("clip", sc["id"], flush=True)
    open(os.path.join(ep, "clips.txt"), "w").write("\n".join(lst))
    body = os.path.join(ep, "body.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(ep, "clips.txt"), "-c", "copy", body])
    total = sum(s["duration"] for s in scenes)
    # quiet sea-like ambience bed: low-passed brown noise with slow swell, mixed well under the voice
    final = os.path.join(ep, "final.mp4")
    run(["ffmpeg", "-y", "-i", body,
         "-f", "lavfi", "-t", f"{total:.2f}", "-i", "anoisesrc=color=brown:amplitude=0.6:sample_rate=48000",
         "-filter_complex",
         "[1:a]lowpass=f=420,highpass=f=40,volume='0.10+0.05*sin(2*PI*t/9)':eval=frame,"
         "afade=t=in:d=3,afade=t=out:st=" + f"{total - 4:.2f}" + ":d=4,aformat=channel_layouts=stereo[bed];"
         "[0:a][bed]amix=inputs=2:duration=first:weights='1 0.6':normalize=0,loudnorm=I=-15:TP=-1.5:LRA=11[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", final])
    print("FINAL", final, round(total / 60, 2), "min")


if __name__ == "__main__":
    main(sys.argv[1])
