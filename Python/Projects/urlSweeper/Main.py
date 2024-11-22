from os import system
from threading import Thread

Thread(
    target=system, args=["websocat -v -E -t ws-l:127.0.0.1:1234 broadcast:mirror:"]
).start()
print("make sure visualize.html is open in your browser")
system(
    f"bbot -t {input("enter url to start scan: ")} -om websocket -c dns.search_distance=10 scope.report_distance=10 modules.websocket.url=ws://127.0.0.1:8765"
)

# websocat -v -E -t ws-l:127.0.0.1:1234 broadcast:mirror:
# american-heritage.instructure.com amazon.com youtube.com google.com cloudflare.com dns.google.com 8.8.8.8 gmail.com tesla.com
# bbot -t apple.com -om websocket -c dns.search_distance=100 scope.report_distance=100 modules.websocket.url=ws://127.0.0.1:1234
