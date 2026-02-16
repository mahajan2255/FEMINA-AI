import uvicorn
import os
import sys

# Ensure the current directory is in the path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    print("Starting System...")
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        print(f"Failed to start server: {e}")
        input("Press Enter to exit...")
