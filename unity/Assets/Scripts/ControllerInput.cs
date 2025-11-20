using System.Collections.Generic;
using UnityEngine;


public class MenuController : MonoBehaviour
{
    public GameObject settingsMenu; // Assign your settings menu Canvas in Inspector
    private bool isMenuOpen = false;


    //Main update function. Checks for OVR input. If Y or B pressed, toggle menu
    void Update()
    {

        OVRInput.Update();

        // Use the Y button (left controller) or B button (right controller) to toggle menu
        if (OVRInput.GetDown(OVRInput.Button.Two)) // Button.Two = Y on left, B on right
        {
            ToggleMenu();
        }
    }

    //Toggles menu active status
    void ToggleMenu()
    {
        isMenuOpen = !isMenuOpen;
        settingsMenu.SetActive(isMenuOpen);
    }
}
