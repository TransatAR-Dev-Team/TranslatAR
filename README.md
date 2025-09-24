# TranslatAR

## Set Up

### Prerequisites

- About 50 GB of free space. This is for:
    - Docker Desktop
    - Docker images
    - Unity Hub
    - Unity Editor
- Docker installled. The easiest way is to install [Docker Desktop](https://docs.docker.com/desktop/). You can also install the [CLI tool](https://docs.docker.com/engine/install/).

- [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html) installed
    - Unity version `2023.3.62f1` installed (instructions in [Set Up](#set-up).

- For headset simulator, Windows or Apple silicon Mac machine.
    > The simulator cannot run on Linux machines or Intel Macs.

    > A physical Meta Quest 3 will run the Unity app regardless of the development environment.

<a id="gpu"></a>
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

    > ***Only*** use the GPU acceleration command if you have an CUDA-capable NVIDIA GPU. [Read more here](#gpu).

    > Docker caches downloaded images and the layers of built images. Only altered layers will be rebuilt with `docker compose up --build`. Building and starting the images will be faster the second time

2. Go to <http://localhost:5173> to see the webpage.

3. Go to <http://localhost:8000/api/data> or <http://localhost:8000/api/db-hello> to fetch data from backend.

Run `docker compose down` to shut it off.

### Unity frontend

1. Install [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html)

2. Open *Projects* tab and click *Add ⌄*

3. In the dropdown, select *Add project from disk*

4. Locate this repository in your file system and select the `unity` directory

5. Download Unity version `2023.3.62f1` from pop up. It should be the reccomended version. 

6. In the pop up, select *Android build support" to be installed as well.

7. Click *Install*. This may take a while to download.

8. Open the project in Unity Hub from the "Projects" list. The project should look like a blank 3D area with a floating text box.

9. In the Unity Editor's taskbar, check *Meta* > *Meta XR Simulator* > *Activate*

    > Leaving *Meta XR Simulator* set to *Deactivate* only renders the subtitle box and saves resources.

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

5. Run this to demonstrate transcription/translation:
    ```sh
    curl -X POST http://localhost:8000/api/process-audio -F "audio_file=@test.wav" -F "source_lang=en" -F "target_lang=es"
    ```

    The output should look like:
    ```log
    {"original_text":"Hello, this is a test.","translated_text":"Hola, esto es una prueba."}
    ```

### Data flow demonstrated

1. The Unity frontend sends a request to the backend API endpoint

2. The backend retrieves data from the MongoDB database

3. The backend responds to Unity with the data

4. Unity receives the response, logs the message in the console, and displays it in the UI

5. The client sends an audio file to the backend server

6. The STT service processes audio using the Whisper model and return transcribed text to the backend

7. The backend sends transcribed text to translation service

8. The translation service sends translated text to the backend 

9. The backend returns translated text to the client

### Demo clean up

Press the "Stop" button (`⏹`) next to the "Play" button to stop the scene.
Run `docker compose down` to shut off Docker containers.
