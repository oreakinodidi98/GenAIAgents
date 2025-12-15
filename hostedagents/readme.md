# Instructions

- Build the container: `docker build -t myagent -f hostedagent/Dockerfile agent/.`
- Run: `docker run -d --name myagent -p 8088:8088 --gpus all myagent`
- Test: `curl -X POST http://localhost:8088/responses -H "Content-Type: application/json" -d '{"input": "Where is Paris?", "stream": false}'`