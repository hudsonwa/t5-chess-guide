# 018 Device sync client
Round 4. Status: built; logic verified end to end over the USB bridge; Wi-Fi transport untested.
Background task: pull on open, push after each save, follow newer remote positions without echoing them.
sync_e2e.py: device follows web on open, device move reaches service, web opens at device position, web move reaches service, device follows on reopen: 5/5 PASS.
Wi-Fi transport needs a saved network on the device (Settings > System > WiFi Networks)

State: open (Wi-Fi transport untested)
