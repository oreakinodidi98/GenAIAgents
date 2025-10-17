# Project overview

1. Create Chat bot Locally
2. Docker container
3. Take to ACR
4. Deploy to ACI 

## process

1. Set up Virtual enviroment ```python -m venv agent_env``` then ```agent_env\Scripts\activate```
2. Install needed packages insall ```pip install -q langchain langchain_experimental openai python-dotenv langchain_openai```
3. install requirements package ```pip install -r requirements.txt```
4. Go to frontend use ```pnpm run setup``` to build main app inside API folder )API-> Static -> react -> assets)
   1. Install pnpm via npm (if you have Node.js installed) ```npm install -g pnpm```
5. use ```azd login``` for developer credentials
   1. Install Azure Developer CLI ```winget install microsoft.azd```
   2. Verify azd is installed ```azd version```
   3. Login to Azure (this will open browser for authentication ```azd login```
   4. Verify login status ```azd auth login-status```
6. Run with uvicorn for development ```uvicorn api.main:create_app --factory --host 0.0.0.0 --port 8000 --reload```
7. need to give mysef role of ```Search Index Data Reader``` in azure for search
8. Build dockerfile using ```docker build -t <name:latest> .```
9. 