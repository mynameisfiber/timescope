AVIFILES := $(wildcard $(*.avi))


%.gif: %.avi
	@echo "BUILDING $@ USING $<"
	ffmpeg -i $< -s 300x200 -pix_fmt rgb24 -r 10 -f gif - | gifsicle --optimize=9 --delay=10 > $@
