# 010 Idle clean-up refresh (~1.5 s) blocks a tap that lands during it
Round 2. Status: mitigated in round 2.
Fix: clean-up only after 15 fast frames and 20 s idle, with epd_fast (614 ms). A collision is now rare and costs at most ~0.6 s.

State: closed (mitigated)
