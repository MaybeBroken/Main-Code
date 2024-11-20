from os import system
from threading import Thread

Thread(
    target=system, args=["websocat -v -E -t ws-l:127.0.0.1:8765 broadcast:mirror:"]
).start()
print("make sure visualize.html is open in your browser")
system(
    f"bbot -t {input("enter url to start scan: ")} -om websocket -c dns.search_distance=10 scope.report_distance=10 modules.websocket.url=ws://127.0.0.1:8765"
)
