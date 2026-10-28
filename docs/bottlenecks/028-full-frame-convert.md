# 028 A full-screen push converts and diffs the whole frame (20 ms)
Loop 2 round 1, rank 6. Status: partly fixed (round 5: no diff on the first frame). The convert itself is PSRAM write bandwidth (~250 KB in 9 ms); aligned 32-bit stores were tried and made no difference, so reverted.

State: closed
