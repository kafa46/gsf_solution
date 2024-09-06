export FLASK_APP=server
export FLASK_DEBUG=True
flask run -h 0.0.0.0 -p 8877

# fast api run 
# cd ../fastapi_server/
# uvicorn main:app --reload --host 0.0.0.0 --port 8899