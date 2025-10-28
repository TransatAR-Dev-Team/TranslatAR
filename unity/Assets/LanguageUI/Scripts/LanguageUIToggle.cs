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
        // input detection
        bool controllerToggle = OVRInput.GetDown(OVRInput.Button.Two);
        bool keyboardToggle = Input.GetKeyDown(KeyCode.N);

        if (controllerToggle || keyboardToggle)
        {
            isVisible = !isVisible;
            languageUI.SetActive(isVisible);
            Debug.Log(isVisible ? "[LanguageUIToggle] Menu opened" : "[LanguageUIToggle] Menu closed");
        }
    }
}
