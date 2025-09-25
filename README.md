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
    - Unity version `2023.3.62f1` installed (instructions in [Set Up: Unity frontend](#unity)).

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

2. Go to <http://localhost:5173> to see the web portal.

3. Go to <http://localhost:8000/api/db-hello> to fetch data from backend.

Run `docker compose down` to shut it off.

<a id="unity"></a>
### Unity frontend

1. Install [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html)

2. Open *Projects* tab and click *Add ⌄*

3. In the dropdown, select *Add project from disk*

4. Locate this repository in your file system and select the `unity` directory

5. Download Unity version `2023.3.62f1` from the pop up. It should be the reccomended version. 

6. In the pop up, select *Android build support" to be installed as well.

7. Click *Install*. This may take a while to download.

8. Open the project in Unity Hub from the "Projects" list. The project should look like a blank 3D area with a floating text box.

9. In the Unity Editor's taskbar, check *Meta* > *Meta XR Simulator* > *Activate*

    > Leaving *Meta XR Simulator* set to *Deactivate* only renders the subtitle box and saves resources.

## Demo

### Running the demo

To demonstrate the connection between the containerized backend and the Unity frontend, first ensure all [Set Up](#set-up) steps are completed.

1. Press the "Play" button (`▶`) at the top center of the Unity editor window to start the scene

2. A pop up with the head set simulator should appear. There should be text on the simulator screen reading: *"Hola, esto es una prueba."*, which is the Spanish translation of "Hello, this is a test." Walk around with `W`, `A`, `S`, and `D` keys. Look around with the arrow keys.

3. Open the Unity console by selecting `Window > General > Console`, or press `Ctrl` + `Shift` + `C`

4. Observe the log. If everything has gone right, it will read:

    ```log
    Received from backend: {"original_text": "Hello, this is a test", "translated_text": "Hola, esto es una prueba."}
    ```

5. Go to <http://localhost:5173> to see the web portal. The translation log will be displayed.

6. Run the scene again and refresh the web portal. Another log will be displayed on the web portal.

### Data flow demonstrated

1. The Unity frontend sends an audio file which says "Hello, this is a test" as a bitstream to the backend

2. The backend sends the audio file to the STT service

3. The STT service processes audio using the Whisper model and return transcribed text to the backend

4. The backend sends transcribed text to translation service

5. The translation service sends translated text to the backend 

6. The backend saves the log to the database

7. The backend returns the transcribed text and the translated text to Unity

8. Unity receives the response, logs the message in the console, and displays the translation in the UI

9. The web portal makes a request to view the translation history

10. The backend fetches the conversation history from the database

11. The backend returns the conversation history to the web portal

12. The web portal displays the converation history

13. Steps 1 through 12 repeated

### Demo clean up

Press the "Stop" button (`⏹`) next to the "Play" button to stop the scene.
Run `docker compose down` to shut off Docker containers.
