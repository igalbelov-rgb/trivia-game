from prometheus_client import Counter, start_http_server

c = Counter("trivia_game_requests", "Number of requests")

start_http_server(8000)