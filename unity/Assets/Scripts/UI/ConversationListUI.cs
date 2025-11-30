using UnityEngine;
using UnityEngine.UI;
using System.Collections.Generic;
using TMPro;

/// <summary>
/// Component that displays the list of translations in a conversation.
/// Manages translated texts as a scrollable list.
/// </summary>
public class ConversationListUI : MonoBehaviour
{
    [Header("UI References")]
    /// <summary>
    /// ScrollView's Content Transform - parent object where translation items are added
    /// </summary>
    public Transform contentParent;

    /// <summary>
    /// Translation item prefab - prefab with TranslationListItem component
    /// </summary>
    public GameObject translationItemPrefab;

    /// <summary>
    /// ScrollRect reference (for auto-scrolling)
    /// </summary>
    public ScrollRect scrollRect;

    [Header("Settings")]
    /// <summary>
    /// Maximum number of items to display on screen
    /// </summary>
    public int maxDisplayedItems = 20;

    /// <summary>
    /// Whether to auto-scroll to bottom when new item is added
    /// </summary>
    public bool autoScrollToBottom = true;

    /// <summary>
    /// List of currently displayed translation items
    /// </summary>
    private List<TranslationListItem> displayedItems = new List<TranslationListItem>();

    /// <summary>
    /// Translation data queue (maintains max count)
    /// </summary>
    private Queue<TranslationData> translationQueue = new Queue<TranslationData>();

    /// <summary>
    /// Current conversation ID
    /// </summary>
    private string currentConversationId;

    /// <summary>
    /// Singleton instance
    /// </summary>
    public static ConversationListUI Instance { get; private set; }

    /// <summary>
    /// Initialize singleton
    /// </summary>
    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
        }
        else
        {
            Destroy(gameObject);
        }
    }

    /// <summary>
    /// Add a new translation to the list
    /// </summary>
    /// <param name="originalText">Original text</param>
    /// <param name="translatedText">Translated text</param>
    /// <param name="conversationId">Conversation ID (optional)</param>
    public void AddTranslation(string originalText, string translatedText, string conversationId = null)
    {
        // Ignore empty text
        if (string.IsNullOrEmpty(originalText) && string.IsNullOrEmpty(translatedText))
        {
            return;
        }

        // Clear list when new conversation starts
        if (!string.IsNullOrEmpty(conversationId) && conversationId != currentConversationId)
        {
            if (!string.IsNullOrEmpty(currentConversationId))
            {
                ClearConversation();
            }
            currentConversationId = conversationId;
        }

        var data = new TranslationData
        {
            OriginalText = originalText,
            TranslatedText = translatedText,
            Timestamp = System.DateTime.Now,
            ConversationId = conversationId
        };

        translationQueue.Enqueue(data);

        // Remove old items when exceeding max count
        while (translationQueue.Count > maxDisplayedItems)
        {
            translationQueue.Dequeue();
        }

        RefreshUI();
    }

    /// <summary>
    /// Clear the list when starting a new conversation
    /// </summary>
    public void ClearConversation()
    {
        translationQueue.Clear();
        currentConversationId = null;
        RefreshUI();
        Debug.Log("[ConversationListUI] Conversation cleared");
    }

    /// <summary>
    /// Refresh UI - recreate all items
    /// </summary>
    private void RefreshUI()
    {
        if (contentParent == null)
        {
            Debug.LogWarning("[ConversationListUI] Content parent is not assigned!");
            return;
        }

        // Remove existing items
        foreach (Transform child in contentParent)
        {
            Destroy(child.gameObject);
        }
        displayedItems.Clear();

        // Verify prefab
        if (translationItemPrefab == null)
        {
            Debug.LogWarning("[ConversationListUI] Translation item prefab is not assigned!");
            return;
        }

        // Create new items
        foreach (var data in translationQueue)
        {
            var itemObj = Instantiate(translationItemPrefab, contentParent);
            var listItem = itemObj.GetComponent<TranslationListItem>();

            if (listItem != null)
            {
                listItem.SetData(data);
                displayedItems.Add(listItem);
            }
            else
            {
                Debug.LogWarning("[ConversationListUI] TranslationListItem component not found on prefab!");
            }
        }

        // Auto-scroll
        if (autoScrollToBottom && scrollRect != null)
        {
            Canvas.ForceUpdateCanvases();
            scrollRect.verticalNormalizedPosition = 0f;
        }
    }

    /// <summary>
    /// Get translation count for current conversation
    /// </summary>
    public int GetTranslationCount()
    {
        return translationQueue.Count;
    }

    /// <summary>
    /// Get current conversation ID
    /// </summary>
    public string GetCurrentConversationId()
    {
        return currentConversationId;
    }

    /// <summary>
    /// Toggle UI visibility
    /// </summary>
    public void ToggleVisibility()
    {
        gameObject.SetActive(!gameObject.activeSelf);
    }

    /// <summary>
    /// Show UI
    /// </summary>
    public void Show()
    {
        gameObject.SetActive(true);
    }

    /// <summary>
    /// Hide UI
    /// </summary>
    public void Hide()
    {
        gameObject.SetActive(false);
    }
}

/// <summary>
/// Struct containing translation data
/// </summary>
[System.Serializable]
public class TranslationData
{
    /// <summary>
    /// Original text
    /// </summary>
    public string OriginalText;

    /// <summary>
    /// Translated text
    /// </summary>
    public string TranslatedText;

    /// <summary>
    /// Translation timestamp
    /// </summary>
    public System.DateTime Timestamp;

    /// <summary>
    /// Conversation ID
    /// </summary>
    public string ConversationId;
}
