from prometheus_client import start_http_server, Counter

c = Counter('trivia_game_requests', 'Number of requests')

start_http_server(8000)