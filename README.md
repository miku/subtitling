README
======

Downcase all MOVs to movs:

    $ find 1-20-S-2-38-S -name "*.MOV" -exec sh -c 'mv "$1" "${1%.MOV}.mov"' _ {} \;

Concatenate videos (well, ...):

	$ # mencoder -oac copy -ovc copy 1-20-S-2-38-S/VIDE0001.mov 1-20-S-2-38-S/VIDE0002.mov -o 1-20-S-2-38-S.mov
	$ # mencoder -oac copy -ovc copy -of avi -o output.avi 1-20-S-2-38-S/VIDE0001.mov 1-20-S-2-38-S/VIDE0002.mov
	$ # MP4Box -cat 1-20-S-2-38-S/VIDE0001.mov -cat 1-20-S-2-38-S/VIDE0002.mov output.m4v

	$ ffmpeg -i 1-20-S-2-38-S/VIDE0001.mov -c copy -bsf h264_mp4toannexb a.ts
	$ ffmpeg -i 1-20-S-2-38-S/VIDE0002.mov -c copy -bsf h264_mp4toannexb b.ts
	$ ffmpeg -i "concat:a.ts|b.ts" -c copy -bsf aac_adtstoasc ab.mp4 && rm a.ts b.ts

Test the subtitles:

	$ mplayer -sub sample.srt galactic_timelapse.avi

Add subtitles:

	$ MP4Box -add ab.mp4#audio -add ab.mp4#video -add test.srt:hdlr=sbtl:lang=en:group=2:layer=-1 -new ab-with-subs.m4v
