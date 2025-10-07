# Unity - TranslatAR

This directory contains the Unity frontend for the TranslatAR project. It is a VR/AR application built with **Unity 2023.3.62f1** that runs on the Meta Quest 3 headset or in the Unity Editor with the Meta XR Simulator. The Unity app connects to the containerized backend services to display real-time translations.

## Tech Stack

- [Unity](https://unity.com/): Version `2023.3.62f1`
- [C#](https://learn.microsoft.com/en-us/dotnet/csharp/): Scripting language for Unity
- [Meta XR SDK](https://developer.oculus.com/downloads/): Provides Quest 3 support and XR Simulator
- [Unity Package Manager](https://docs.unity3d.com/Manual/upm-ui.html): Dependency management

## Prerequisites

- [Unity Hub](https://docs.unity3d.com/hub/manual/InstallHub.html) installed
- Unity version `2023.3.62f1` with **Android Build Support** (and subcomponents) installed
- Windows PC or Apple Silicon Mac
  > Not supported on Linux or Intel Macs  
- A physical Meta Quest 3 headset, or use the **Meta XR Simulator** in the Unity Editor

## Getting Started

See the `README.md` in the root of the project for instructions on building and running the entire project.

1. Open Unity Hub
2. Add this project: *Projects > Add project from disk* → select the `unity/` directory
3. If prompted, download and install Unity `2023.3.62f1` with Android build support
4. Open the project in Unity Hub
5. In the Unity Editor, activate the XR simulator: *Meta > Meta XR Simulator > Activate*
6. Press ▶ (Play) to run the scene

## Testing

This project uses the **Unity Test Framework** for running tests directly inside the Unity Editor. Tests are located in the `Assets/Tests` directory.

Tests are separated into two types:

- **Edit Mode**: Fast-running tests for logic and utility functions that don't require a running scene.
- **Play Mode**: Tests that run in a scene, allowing for the testing of `MonoBehaviour`s, coroutines, and component interactions.

### How to Run Tests

1. In the Unity Editor, open the Test Runner window by navigating to **Window > General > Test Runner**.
2. In the Test Runner window, you will see two tabs: `PlayMode` and `EditMode`.
3. Click on a tab and press the **Run All** button to execute all tests in that category.

## Managing Dependencies

Dependencies are handled through Unity’s Package Manager.  
To add, update, or remove a package:  
1. Open Unity Editor
2. Go to *Window > Package Manager*  
3. Make changes, then commit the updated `Packages/manifest.json` and `Packages/packages-lock.json` files  

> Do **not** commit the `Library/` or `Builds/` directories. They are machine-specific.  
