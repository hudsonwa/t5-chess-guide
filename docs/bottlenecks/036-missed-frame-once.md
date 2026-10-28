# 036 One press in 12 test runs produced no frame
Found while preparing the public release. Status: open, not reproduced.
input_reliability.py (15 presses, 150 ms apart) timed out waiting for a frame once, right after consistency.py, in the full regression. 11 later runs pass, including that exact order three times with the device log captured. Next step if it recurs: the captured log (ir_dbg) shows whether the touch arrived.

State: open
