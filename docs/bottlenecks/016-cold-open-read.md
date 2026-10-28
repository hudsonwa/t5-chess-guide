# 016 Opening the guide reads the whole 0.5 MB data file first
Round 4, rank 2 (811 ms). Status: fixed in round 4.
The SD card manages ~640 KB/s (chunking through internal RAM made no difference). Fix: read only header, sprites, game names and the current game (155 ms); other games load during idle time or on demand (~25 ms).

State: closed
