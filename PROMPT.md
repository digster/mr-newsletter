
---

## Fix Desktop App Build and Run Issues

Implement fixes for:
1. `make build` failing with EOFError due to interactive prompt - add `-y` flag
2. `make run` failing with 'Address already in use' on port 8550 - add `kill` target
