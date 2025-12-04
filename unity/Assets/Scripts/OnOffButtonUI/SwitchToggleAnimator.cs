using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System.Collections;

// makes the toggle look like a switch with a sliding knob and ON/OFF text
public class SwitchToggleAnimator : MonoBehaviour
{
    [Header("Switch Visual Elements")]
    [Tooltip("The knob that slides (the Checkmark Image)")]
    [SerializeField] private RectTransform knob;
    
    [Tooltip("The background track (the Background Image)")]
    [SerializeField] private Image backgroundImage;
    
    [Header("Colors")]
    [Tooltip("Background color when toggle is OFF")]
    [SerializeField] private Color offColor = new Color(0.8f, 0.2f, 0.2f, 1f); // Red
    
    [Tooltip("Background color when toggle is ON")]
    [SerializeField] private Color onColor = new Color(0.2f, 0.2f, 0.2f, 1f); // Dark gray
    
    [Header("Text Labels")]
    [Tooltip("Text that shows 'OFF' when toggle is off")]
    [SerializeField] private TextMeshProUGUI offText;
    
    [Tooltip("Text that shows 'ON' when toggle is on")]
    [SerializeField] private TextMeshProUGUI onText;
    
    [Header("Animation")]
    [Tooltip("Animation duration in seconds")]
    [SerializeField] private float animationDuration = 0.2f;
    
    // reference to the Unity Toggle component
    private Toggle toggle;
    
    // calculated positions for the knob (left = off, right = on)
    private Vector2 offPosition;
    private Vector2 onPosition;
    
    // keeps track of the animation coroutine so we can stop it if needed
    private Coroutine animationCoroutine;

    void Start()
    {
        // get the toggle component on this GameObject
        toggle = GetComponent<Toggle>();
        
        if (toggle == null)
        {
            Debug.LogError("[SwitchToggleAnimator] Toggle component not found!");
            return;
        }
        
        // auto-find components if not assigned in inspector
        if (knob == null)
        {
            Transform checkmark = transform.Find("Checkmark");
            if (checkmark != null)
            {
                knob = checkmark.GetComponent<RectTransform>();
            }
        }
        
        if (backgroundImage == null)
        {
            Transform background = transform.Find("Background");
            if (background != null)
            {
                backgroundImage = background.GetComponent<Image>();
            }
        }
        
        // calculate where the knob should be positioned for on/off states
        if (knob != null && backgroundImage != null)
        {
            RectTransform backgroundRect = backgroundImage.GetComponent<RectTransform>();
            float trackWidth = backgroundRect.rect.width;
            float knobWidth = knob.rect.width;
            float padding = 2f; // small padding from edges
            
            // preserve the knob's current Y position (so it doesn't move vertically)
            float knobY = knob.anchoredPosition.y;
            
            // off position: knob on the left side of the track
            offPosition = new Vector2(-trackWidth / 2 + knobWidth / 2 + padding, knobY);
            // on position: knob on the right side of the track
            onPosition = new Vector2(trackWidth / 2 - knobWidth / 2 - padding, knobY);
        }
        
        // connect to toggle events
        toggle.onValueChanged.AddListener(OnToggleValueChanged);
        
        // set the initial visual state
        UpdateSwitchVisual(toggle.isOn, false);
    }
    
    void OnDestroy()
    {
        // clean up event listener to prevent memory leaks
        if (toggle != null)
        {
            toggle.onValueChanged.RemoveListener(OnToggleValueChanged);
        }
    }
    
    // called when user clicks the toggle
    private void OnToggleValueChanged(bool isOn)
    {
        UpdateSwitchVisual(isOn, true);
    }
    
    // updates the switch visual state (with or without animation)
    private void UpdateSwitchVisual(bool isOn, bool animate)
    {
        // stop any existing animation first
        if (animationCoroutine != null)
        {
            StopCoroutine(animationCoroutine);
        }
        
        if (animate)
        {
            // animate the switch smoothly
            animationCoroutine = StartCoroutine(AnimateSwitch(isOn));
        }
        else
        {
            // set state immediately (used on startup)
            SetSwitchState(isOn);
        }
    }
    
    // smoothly animates the switch from current state to target state
    private IEnumerator AnimateSwitch(bool targetState)
    {
        if (knob == null || backgroundImage == null) yield break;
        
        // remember starting positions and colors
        Vector2 startPos = knob.anchoredPosition;
        Vector2 targetPos = targetState ? onPosition : offPosition;
        Color startColor = backgroundImage.color;
        Color targetColor = targetState ? onColor : offColor;
        
        float elapsed = 0f;
        
        // animate over time
        while (elapsed < animationDuration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / animationDuration);
            // apply smooth easing for better animation feel
            t = t * t * (3f - 2f * t);
            
            // smoothly move knob and change background color
            knob.anchoredPosition = Vector2.Lerp(startPos, targetPos, t);
            backgroundImage.color = Color.Lerp(startColor, targetColor, t);
            
            yield return null;
        }
        
        // make sure we end up exactly in the right state (in case of rounding errors)
        SetSwitchState(targetState);
    }
    
    // sets the switch to a specific state (no animation)
    private void SetSwitchState(bool isOn)
    {
        // move knob to correct position
        if (knob != null)
        {
            knob.anchoredPosition = isOn ? onPosition : offPosition;
        }
        
        // change background color
        if (backgroundImage != null)
        {
            backgroundImage.color = isOn ? onColor : offColor;
        }
        
        // show/hide text labels based on state
        if (offText != null)
        {
            offText.gameObject.SetActive(!isOn);
        }
        
        if (onText != null)
        {
            onText.gameObject.SetActive(isOn);
        }
    }
}

