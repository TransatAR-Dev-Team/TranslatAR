using UnityEngine;

public class LanguageUIToggle : MonoBehaviour
{
    [Header("Assign the LanguageUI Canvas GameObject")]
    [SerializeField] private GameObject languageUI;

    private bool isVisible = true;

    void Start()
    {
        if (!languageUI)
        {
            Debug.LogWarning("[LanguageUIToggle] LanguageUI not assigned.");
            return;
        }

        isVisible = languageUI.activeSelf;
    }

    void Update()
    {
        // detect input keys
        if (Input.GetKeyDown(KeyCode.L) || Input.GetKeyDown(KeyCode.JoystickButton1))
        {
            isVisible = !isVisible;
            languageUI.SetActive(isVisible);

            if (isVisible)
                Debug.Log("[LanguageUIToggle] Menu opened");
            else
                Debug.Log("[LanguageUIToggle] Menu closed");
        }
    }
}
