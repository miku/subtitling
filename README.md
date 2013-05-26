README
======

0. Downcase all filenames (`MOV` to `mov`). (Might only be a problem on HFS+):

    $ find 1-20-S-2-38-S -name "*.MOV" \
        -exec sh -c 'mv "$1" "${1%.MOV}.mov"' _ {} \;

1. *Concatenate* videos via [ffmpeg](http://www.ffmpeg.org/) and [MPEG transport stream](http://en.wikipedia.org/wiki/MPEG_transport_stream):

    $ ffmpeg -i 1-20-S-2-38-S/VIDE0001.mov -c copy -bsf h264_mp4toannexb a.ts
    $ ffmpeg -i 1-20-S-2-38-S/VIDE0002.mov -c copy -bsf h264_mp4toannexb b.ts
    $ ffmpeg -i "concat:a.ts|b.ts" -c copy -bsf aac_adtstoasc ab.mp4

2. *Test* the subtitles with [mplayer](http://www.mplayerhq.hu/):

    $ mplayer -sub sample.srt galactic_timelapse.avi

3. *Create a new file* that has a dedicated subtitle track with [MP4Box](http://gpac.wp.mines-telecom.fr/mp4box/):

    $ MP4Box -add ab.mp4#audio -add ab.mp4#video \
        -add test.srt:hdlr=sbtl:lang=en:group=2:layer=-1 -new ab-with-subs.m4v


Failed attempts
---------------

Just some things that seemed to work, but don't.

    $ # mencoder -oac copy -ovc copy \
        1-20-S-2-38-S/VIDE0001.mov 1-20-S-2-38-S/VIDE0002.mov \
        -o 1-20-S-2-38-S.mov

    $ # mencoder -oac copy -ovc copy \
        -of avi -o output.avi \
        1-20-S-2-38-S/VIDE0001.mov 1-20-S-2-38-S/VIDE0002.mov

    $ # MP4Box -cat 1-20-S-2-38-S/VIDE0001.mov -cat 1-20-S-2-38-S/VIDE0002.mov \
        output.m4v
