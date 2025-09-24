# TranslatAR

## Set Up

### Prerequisites

- About 50 GB of free space. This is for:
    - Docker Desktop
    - Docker images
    - Unity Hub
    - Unity Editor
<a id="gpu"></a>
- Docker installled. The easiest way is to install [Docker Desktop](https://docs.docker.com/desktop/). You can also install the [CLI tool](https://docs.docker.com/engine/install/).

- [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html) installed
    - Unity version `2023.2.20f1` installed


- For GPU acceleration, a [CUDA-capable NVIDIA GPU](https://developer.nvidia.com/cuda-gpus)
    > Hint: If you're using a Mac, you don't have a CUDA-capable GPU.

### Docker containers

1. Use `docker compose` to start everything. Initially donwloading the images may take a while. Use:

    ```sh
    # This runs everything on your CPU
    docker compose up --build -d
    ```
   
    Or, to use GPU acceleration for STT service:
    
    ```sh
    # This layers the GPU config on top of the base config and enables GPU acceleration
    docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build -d
    ```

    > ***Only*** use the above command if you have an CUDA-capable NVIDIA GPU. [Read more here](#gpu).

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
2. A pop up with the head set simulator should appear. There should be text on the simulator screen reading: *"Hello from MongoDB!"* Walk around with `W`, `A`, `S`, and `D` keys. Look around with the arrow keys.
3. Open the Unity console by selecting `Window > General > Console`, or press `Ctrl` + `Shift` + `C`
4. Observe the log. If everything has gone right, it will read:

    ```log
    Received from backend: {"message":"Hello from MongoDB!"}
    Message from backend: Hello from MongoDB!
    ```

5. Run this to demonstrate transcription:
    ```sh
    curl -X POST -F "audio_file=@test.wav" http://localhost:9000/transcribe
    ```
    The output should read:
    ```log
    {"transcription":"Hello, this is a test."}
    ```

6. Run this to demonstrate translation:
    ```sh
    curl -X POST "http://localhost:9001/translate" -H "Content-Type: application/json" -d '{"text": "Hello, world!", "source_lang": "en", "target_lang": "es"}'
    ```

    The output should look like:
    ```log
    {"translated_text":"¡Hola, mundo!"}



### Data flow demonstrated

1. The Unity frontend sends a request to the backend API endpoint
2. The backend retrieves data from the MongoDB database
3. The backend responds to Unity with the data
4. Unity receives the response, logs the message in the console, and displays it in the UI.
5. The STT service provides an accurate transcription.
6. The Translation service provides an accurate translation

### Demo clean up

Press the "Stop" button (`⏹`) next to the "Play" button to stop the scene.
Run `docker compose down` to shut off Docker containers.
