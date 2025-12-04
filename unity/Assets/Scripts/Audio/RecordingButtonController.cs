using UnityEngine;
using UnityEngine.UI;

// Handles the recording button click to toggle audio recording.
// Attach this script to a UI Button that should start/stop recording.

public class RecordingButtonController : MonoBehaviour
{
    [Header("Audio Recording Manager")]
    [Tooltip("Reference to the AudioRecordingManager component that manages recording")]
    [SerializeField] private AudioRecordingManager audioRecordingManager;

    [Header("Button Reference (Optional)")]
    [Tooltip("The button component. If not assigned, will try to find it on this GameObject")]
    [SerializeField] private Button recordingButton;

    void Start()
    {
        // Try to find AudioRecordingManager if not assigned
        if (audioRecordingManager == null)
        {
            audioRecordingManager = FindObjectOfType<AudioRecordingManager>();
            if (audioRecordingManager == null)
            {
                Debug.LogWarning("[RecordingButtonController] AudioRecordingManager not found. Please assign it in the Inspector.");
            }
        }

        // Try to find Button component if not assigned
        if (recordingButton == null)
        {
            recordingButton = GetComponent<Button>();
        }

        // Wire up the button click event
        if (recordingButton != null)
        {
            recordingButton.onClick.AddListener(OnRecordingButtonClicked);
        }
        else
        {
            Debug.LogWarning("[RecordingButtonController] No Button component found. Please attach this script to a Button GameObject.");
        }
    }

    // Called when the recording button is clicked.
    public void OnRecordingButtonClicked()
    {
        if (audioRecordingManager != null)
        {
            audioRecordingManager.ToggleRecording();
        }
        else
        {
            Debug.LogWarning("[RecordingButtonController] Cannot toggle recording: AudioRecordingManager not assigned.");
        }
    }

    void OnDestroy()
    {
        // Clean up event listener
        if (recordingButton != null)
        {
            recordingButton.onClick.RemoveListener(OnRecordingButtonClicked);
        }
    }
}

