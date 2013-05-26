help:
	cat README.md

1-20-S-2-38-S/VIDE0001.mov:
	echo "sample movie 1st part"

1-20-S-2-38-S/VIDE0002.mov:
	echo "sample movie 2nd part"

sample.csv:
	echo "use xlsx2csv.py or export to CSV from Excel"

a.ts: 1-20-S-2-38-S/VIDE0001.mov
	ffmpeg -i 1-20-S-2-38-S/VIDE0001.mov -c copy -bsf h264_mp4toannexb a.ts

b.ts: 1-20-S-2-38-S/VIDE0002.mov
	ffmpeg -i 1-20-S-2-38-S/VIDE0002.mov -c copy -bsf h264_mp4toannexb b.ts

ab.mp4: a.ts b.ts
	ffmpeg -i "concat:a.ts|b.ts" -c copy -bsf aac_adtstoasc ab.mp4

sample.srt: sample.csv
	python subtitlegen.py -l sample.csv > sample.srt

output.m4v: ab.mp4 sample.srt
	MP4Box -add ab.mp4#audio -add ab.mp4#video -add sample.srt:hdlr=sbtl:lang=en:group=2:layer=-1 -new output.m4v

clean:
	rm -f a.ts
	rm -f b.ts
	rm -f ab.mp4
	rm -f sample.srt
	rm -f output.m4v