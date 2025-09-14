# TranslatAR

## Set Up

### Docker containers

1. Run `docker compose up -d` to start everything. Initially donwloading the images may take a while.
2. Go to <http://localhost:5173> to see the webpage.
3. Go to <http://localhost:8000/api/data> or <http://localhost:8000/api/db-hello> to fetch data from backend.

Run `docker compose down` to shut it off.

### Unity frontend

1. Install [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html)
2. Open *Projects* tab and click *New project*
3. Locate this repository in your file system and select the `unity` directory
4. Download reccomended version of Unity from pop up (this may take a while)
5. Open the project

The project should look like a blank 3D area.

## Demo

### Running the demo

To demonstrate the connection between the containerized backend and the Unity frontend, first ensure all [Set Up](#set-up) steps are completed.

1. Press the "Play" button (`▶`) at the top center of the Unity editor window to start the scene
2. Open the Unity console by selecting `Window > General > Console`, or press `Ctrl` + `Shift` + `C`
3. Observe the log. If everything has gone right, it will read:

    ```log
    Received from backend: {"message":"Hello from MongoDB!"}
    Message from backend: Hello from MongoDB!
    ```

### Data flow demonstrated

1. The Unity frontend sends a request to the backend API endpoint
2. The backend retrieves data from the MongoDB database
3. The backend responds to Unity with the data
4. Unity receives the response and logs the message in the console

### Demo clean up

Press the "Stop" button (`⏹`) next to the "Play" button to stop the scene.
Run `docker compose down` to shut off Docker containers.
