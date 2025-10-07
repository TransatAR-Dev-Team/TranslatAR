# TranslatAR

## Prerequisites

- About 50 GB of free space. This is for:
  - Docker Desktop
  - Docker images
  - Ollama LLM model
  - Unity Hub
  - Unity Editor

- Docker installled. The easiest way is to install [Docker Desktop](https://docs.docker.com/desktop/). You can also install the [CLI tool](https://docs.docker.com/engine/install/).

- [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html) installed
  - Unity version `2022.3.62f1` installed (instructions in [Set Up: Unity frontend](#unity-frontend)).

- For Unity, Windows or Apple silicon Mac machine.

    > The Unity project cannot run on Linux machines or Intel Macs.

    > A physical Meta Quest 3 will run the Unity app regardless of your machine.

<a id="gpu"></a>

- For GPU acceleration:
  - a [CUDA-capable NVIDIA GPU](https://developer.nvidia.com/cuda-gpus)

    > Hint: If you're using a Mac, you don't have a CUDA-capable GPU.
  
  - [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) installed.  

## Set Up

> If you'd like to know how to run docker containers directly in VS Code read this [document on .devcontainer setup](docs/dev_container.md)

### Initial set up

First, ensure all [prerequisites](#prerequisites) are met.

1. Clone this repository and set working directory to project directory:

    ```sh
    git clone https://github.com/TransatAR-Dev-Team/TranslatAR.git ; cd TranslatAR
    ```

### Docker containers

1. Use `docker compose` to start everything. Initially downloading the images may take a while. Use:

    ```sh
    # This runs everything on your CPU
    docker compose up --build -d
    ```

    Or, to use GPU acceleration for STT and Ollama:

    ```sh
    # This layers the GPU config on top of the base config and enables GPU acceleration
    docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build -d
    ```

    > ***Only*** use the GPU acceleration command if you have an CUDA-capable NVIDIA GPU and NVIDIA Conainer Toolkit installed. [Read more here](#gpu).

    Docker caches downloaded images and the layers of built images. Only altered layers will be rebuilt with `docker compose up --build`. Building and starting the images will be faster the second time

2. Go to <http://localhost:5173> and <http://localhost:8000/api/db-hello> to verify the containers are running.

3. If you haven't, download the LLM model for Ollama. Downloading the model may take a while. **Only run this command if you haven't before.**

    ```sh
    docker exec -it ollama ollama pull phi3:mini
    ```

    > You only have to run this command once. The model is saved to a Docker volume (`ollama-data`).

    > `docker exec -it <container name> <command>` runs the command *inside* the container.

> Run `docker compose down` to shut off all containers. See [Demo clean up](#demo-clean-up).

### Unity frontend

1. Install [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html)

    > Unity Hub has a [CLI tool](https://docs.unity3d.com/hub/manual/HubCLI.html) that can do everything needed to set up the environment. This guide will continue without using the CLI tool.

2. Open *Projects* tab and click *Add ⌄*

3. In the dropdown, select *Add project from disk*

4. Locate this repository in your file system and select the `unity` directory

5. Download Unity version `2022.3.62f1` from the pop up. It should be the recommended version.

6. In the pop up, select *Android build support* and all subitems to be installed as well.

7. Click *Install*. This may take a while to download.

8. Open the project in Unity Hub from the "Projects" list. The project should look like a blank 3D area with a floating text box.

9. In the Unity Editor's taskbar, check *Meta* > *Meta XR Simulator* > *Activate*

    > Leaving *Meta XR Simulator* set to *Deactivate* only renders the subtitle box in 2D and saves resources.

10. Ensure the "Laptop" button next to the transpot buttons is blue. This runs the app on the headset simulator. Example:

    ![Laptop button is selected/blue](docs/images/laptop_button.png)

## Demo

### Running the demo

To demonstrate the connection between the containerized backend and the Unity frontend, first ensure all [Set Up](#set-up) steps are completed.

1. Press the "Play" button (`▶`) at the top center of the Unity editor window to start the scene.

2. A pop up with the headset simulator should appear.

   > The room you see in the pop up simulates the video passthrough feature of a real Meta Quest headset, where you would instead see your actual physical surroundings through the device's cameras.

   The text on the simulator screen will prompt you: *"Press and hold (B) or Left Click to record."*.

   Walk around with `W`, `A`, `S`, and `D` keys. Look around with the arrow keys.

3. **Click your mouse inside the simulator window** to give it focus.

4. **Press and hold the `B` button**. The text will change to *"Recording..."*. Speak into your computer's microphone.

5. **Release the Left Mouse Button**. The text will change to *"Processing audio..."*.

6. After a moment, the text will update with the Spanish translation of what you said.

7. Go to <http://localhost:5173> to see the web portal. The new translation you just created will be at the top of the history log.

8. Repeat steps 4-6 to add more translations. Refresh the web portal to see the history update.

9. Type/copy some text into the "Summarize Text" text box on the web portal. Select a summary length (short, medium, long) and click the "Summarize" button. A summary of the text will be generated.

### Data flow demonstrated

#### Translation

1. The user presses and holds a button in the Unity frontend.

2. Unity captures live audio from the microphone into an audio clip.

3. When the user releases the button, Unity converts the audio clip to a WAV byte stream and sends it to the backend.

4. The backend forwards the audio file to the STT service.

5. The STT service processes the audio using the Whisper model and returns the transcribed text to the backend.

6. The backend sends the transcribed text to the translation service.

7. The translation service returns the translated text to the backend.

8. The backend saves the original text, translated text, and languages to the database.

9. The backend returns the original and translated text to the Unity frontend.

10. Unity receives the response and displays the translated text in the UI.

11. The web portal periodically or manually requests the translation history from the backend.

12. The backend fetches the conversation history from the database and returns it to the web portal.

13. The web portal displays the updated conversation history.

#### Summarization

1. A user on the web portal enters text, selects a summary length, and clicks the "Summarize" button.

2. The web portal sends the text and length preference to the backend's `/api/summarize` endpoint.

3. The backend forwards the request to the `summarization-service`.

4. The `summarization-service` constructs a prompt based on the desired length and text, and sends it to the `ollama` service.

5. The `ollama` service uses its language model (`phi3:mini`) to generate a summary.

6. The `ollama` service returns the generated summary to the `summarization-service`.

7. The `summarization-service` forwards the summary back to the `backend`.

8. The backend returns the summary to the web portal.

9. The web portal UI updates to display the generated summary.

### Demo clean up

1. Press the "Stop" button (`⏹`) next to the "Play" button to stop the scene.

2. Run `docker compose down` to shut off Docker containers.

## Testing

### Testing Docker Containers

To run all tests *except for Unity tests*, use:

```sh
docker compose -f docker-compose.test.yml up --build --exit-code-from test_runner
```

This will build the `test` stage of each service, run its test suite in parallel, and then automatically shut down and clean up.

See [Unity testing instructions](./unity/README.md#testing) to run Unity tests.

```sh
docker compose -f docker-compose.test.yml up --build --exit-code-from test_runner
```

### Running Tests Locally

For rapid development and debugging, you can run tests for individual services on your local machine. Before running tests, you must navigate to the service's directory and install its dependencies.

Instructions for each service can be found at the links below:

- [Web Portal (`web-portal`)](./web-portal/README.md#local-testing)
- [Python Services (`backend`, `stt-service`, `summarization-service`, and `translation-service`)](./docs/developer_guide.python_services.md#local-testing)
- [Unity (`unity`)](./unity/README.md#testing)
