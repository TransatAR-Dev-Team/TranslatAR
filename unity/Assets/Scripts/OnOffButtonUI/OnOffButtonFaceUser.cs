using UnityEngine;

public class OnOffButtonFaceUser : MonoBehaviour
{
    [Header("Target to Face")]
    [Tooltip("Usually CenterEyeAnchor on the OVRCameraRig.")]
    public Transform target;

    [Header("Options")]
    [Tooltip("Keeps the UI upright.")]
    public bool keepUpright = true; // with this the UI will be flat, otherwise it'll have a more VR type of tilt. Can set accordingly to user.

    [Tooltip("Smooth rotation speed (degrees per second). You can play with the numbers.")]
    public float smoothTurn = 0f; // would reccomend 0 or it gets too slow.

    [Header("Menu Canvas")]
    [Tooltip("Assign the Canvas that should face the user.")]
    [SerializeField] private Canvas menuCanvas;

    // --- NEW PUBLIC INITIALIZER for testing and runtime reuse ---
    public void Initialize()
    {
        if (!target && Camera.main)
            target = Camera.main.transform;
    }

    void Start()
    {
        // Call shared initializer
        Initialize();
    }

    void LateUpdate()
    {
        if (!target) return;

        // rotate to face user
        Vector3 direction = transform.position - target.position;

        // keep it upright (if setting checked)
        if (keepUpright)
            direction.y = 0;

        if (direction.sqrMagnitude < 0.001f)
            return;

        // calculate the desired rotation
        Quaternion desiredRotation = Quaternion.LookRotation(direction);

        // smooth or snap rotation depending on settings
        if (smoothTurn > 0f)
        {
            transform.rotation = Quaternion.RotateTowards(
                transform.rotation, desiredRotation, smoothTurn * Time.deltaTime
            );
        }
        else
        {
            transform.rotation = desiredRotation;
        }

        // also rotate the assigned menu canvas to face the user
        if (menuCanvas)
        {
            Vector3 dir = menuCanvas.transform.position - target.position;

            if (keepUpright)
                dir.y = 0;

            if (dir.sqrMagnitude < 0.001f)
                return;

            Quaternion desiredRot = Quaternion.LookRotation(dir);

            if (smoothTurn > 0f)
            {
                menuCanvas.transform.rotation = Quaternion.RotateTowards(
                    menuCanvas.transform.rotation, desiredRot, smoothTurn * Time.deltaTime
                );
            }
            else
            {
                menuCanvas.transform.rotation = desiredRot;
            }
        }
    }
}
