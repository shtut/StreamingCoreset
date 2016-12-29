taskkill /f /im python.exe
start "server" python Server.py
PAUSE
for /l %%x in (1, 1, %1) do (
	start "worker %%x" python Test.py worker 
	PAUSE
)

start "summary worker" python Test.py summary
PAUSE
start "client" python StreamingClient.py