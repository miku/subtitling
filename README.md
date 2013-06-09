README
======

`subtitlegen` creates [SRTs](http://en.wikipedia.org/wiki/SubRip) from 
[CSVs](http://en.wikipedia.org/wiki/Comma-separated_values).

> SRT is perhaps the most basic of all subtitle formats. ([http://www.matroska.org/technical/specs/subtitles/srt.html](http://www.matroska.org/technical/specs/subtitles/srt.html))

1. Create the **subtitles from csv** via `subtitlegen.py`:

        $ python subtitlegen.py --long sample.csv > sample.srt

    The expected CSV format is as follows (note that the time format is `MM:SS:Milliseconds`, although full milliseconds would need three digits):

        $ cat sample.csv
        0,34:39:00
        1,34:52:00
        2,35:01:00
        3,35:55:00
        ...

    The resulting srt looks like (the time format here is `HH:MM:SS,milliseconds`):

        $ cat sample.srt
        0
        00:34:39,000 --> 00:34:51,999
        ~ 0 m [00:34:39,000 | 13.0]

        1
        00:34:52,000 --> 00:35:00,999
        ~ 1 m [00:34:52,000 | 9.0]

        2
        00:35:01,000 --> 00:35:54,999
        ~ 2 m [00:35:01,000 | 54.0]

        3
        00:35:55,000 --> 00:36:11,999
        ~ 3 m [00:35:55,000 | 17.0]

        ...


2. Optional. Downcase all filenames (`MOV` to `mov`); (might only be a problem on HFS+):

        $ find 1-20-S-2-38-S -name "*.MOV" \
            -exec sh -c 'mv "$1" "${1%.MOV}.mov"' _ {} \;


3. **Concatenate** videos via [ffmpeg](http://www.ffmpeg.org/) and [MPEG transport stream](http://en.wikipedia.org/wiki/MPEG_transport_stream):

        $ ffmpeg -i 1-20-S-2-38-S/VIDE0001.mov -c copy -bsf h264_mp4toannexb a.ts
        $ ffmpeg -i 1-20-S-2-38-S/VIDE0002.mov -c copy -bsf h264_mp4toannexb b.ts
        $ ffmpeg -i "concat:a.ts|b.ts" -c copy -bsf aac_adtstoasc ab.mp4


4. **Test** the subtitles with [mplayer](http://www.mplayerhq.hu/):

        $ mplayer -sub sample.srt ab.mp4


5. **Create a new file** that has a dedicated subtitle track with [MP4Box](http://gpac.wp.mines-telecom.fr/mp4box/):

        $ MP4Box -add ab.mp4#audio -add ab.mp4#video \
            -add test.srt:hdlr=sbtl:lang=en:group=2:layer=-1 -new output.m4v

As a picture
------------

![Makefile viz.](http://i.imgur.com/6qHrqgC.png "Makefile viz. Thanks vak (https://github.com/vak/makefile2dot)")

Thanks [vak](https://github.com/vak) for [makefile2dot](https://github.com/vak/makefile2dot).

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
