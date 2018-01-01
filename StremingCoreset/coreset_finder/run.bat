start  D:\Continuum\Anaconda2\python.exe server_runner.py localhost

TIMEOUT /T 3

start  D:\Continuum\Anaconda2\python.exe worker_runner.py localhost

TIMEOUT /T 3

start  D:\Continuum\Anaconda2\python.exe summary_worker_runner.py localhost

TIMEOUT /T 3

start  D:\Continuum\Anaconda2\python.exe client_runner.py localhost 4