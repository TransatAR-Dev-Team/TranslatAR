# 🔐 Unity Google Sign-In Integration

This document describes the Unity Google Sign-In system implemented for the TranslatAR project.

## 📁 **Scripts Overview**

### **Core Scripts:**
- **`GoogleSignInManager.cs`** - Main authentication manager
- **`GoogleSignInUI.cs`** - UI controller for sign-in interface
- **`GoogleSignInConfig.cs`** - Configuration ScriptableObject
- **`GoogleSignInWebGL.cs`** - WebGL-specific OAuth handling
- **`UnityGoogleSignInDemo.cs`** - Demo implementation
- **`GoogleSignInTest.cs`** - Testing utilities

## 🚀 **Features**

### ✅ **Authentication Flow:**
1. **OAuth 2.0** integration with Google
2. **JWT token** management
3. **User profile** data retrieval
4. **Profile picture** loading
5. **WebGL support** for browser builds

### ✅ **Platform Support:**
- **Unity Editor** (for development)
- **WebGL builds** (for browser deployment)
- **Standalone builds** (Windows, Mac, Linux)

## 🔧 **Setup Instructions**

### **1. Backend Configuration:**
Ensure your backend is running with Google OAuth endpoints:
- `GET /auth/google` - Initiate OAuth
- `GET /auth/google/callback` - Handle OAuth callback
- `GET /auth/verify` - Verify JWT tokens

### **2. Unity Setup:**
1. **Add scripts** to your Unity project
2. **Create a GameObject** with `GoogleSignInManager` component
3. **Configure OAuth credentials** in the manager
4. **Set up UI elements** for sign-in interface

### **3. WebGL Configuration:**
For WebGL builds, ensure:
- **JavaScript interop** is properly configured
- **OAuth redirects** are handled correctly
- **CORS settings** allow your domain

## 📱 **Usage Examples**

### **Basic Sign-In:**
```csharp
// Start Google Sign-In process
GoogleSignInManager.Instance.StartGoogleSignIn();

// Check authentication status
bool isSignedIn = GoogleSignInManager.Instance.IsAuthenticated();

// Get current user
string userName = GoogleSignInManager.Instance.GetCurrentUser();
```

### **UI Integration:**
```csharp
// Update UI based on authentication state
if (GoogleSignInManager.Instance.IsAuthenticated())
{
    // Show user profile
    userInfoText.text = GoogleSignInManager.Instance.userName;
}
else
{
    // Show sign-in button
    signInButton.gameObject.SetActive(true);
}
```

## 🧪 **Testing**

### **Test Script:**
Use `GoogleSignInTest.cs` to verify:
- Manager initialization
- Authentication status
- Token validation
- User data retrieval

### **Manual Testing:**
1. **Start the demo scene**
2. **Click "Sign In with Google"**
3. **Complete OAuth in browser**
4. **Verify user profile display**

## 🔒 **Security Considerations**

### **Token Management:**
- **JWT tokens** are used for authentication
- **Tokens expire** after 1 hour
- **Secure storage** recommended for production

### **OAuth Security:**
- **Client ID** is public (safe to expose)
- **Client Secret** must be kept secure
- **Redirect URIs** must be whitelisted

## 🐛 **Troubleshooting**

### **Common Issues:**

#### **"Manager not found":**
- Ensure `GoogleSignInManager` is in the scene
- Check that the component is properly attached

#### **"OAuth popup blocked":**
- Allow popups in your browser
- Check browser security settings

#### **"Token verification failed":**
- Verify backend is running
- Check JWT secret configuration
- Ensure network connectivity

#### **"WebGL not working":**
- Verify JavaScript interop setup
- Check browser console for errors
- Ensure proper CORS configuration

## 📚 **API Reference**

### **GoogleSignInManager:**
- `StartGoogleSignIn()` - Initiate OAuth flow
- `HandleAuthCode(string)` - Process auth code
- `SetAuthToken(string)` - Set JWT token
- `IsAuthenticated()` - Check auth status
- `GetCurrentUser()` - Get user name
- `GetAuthToken()` - Get current token
- `Logout()` - Clear authentication

### **GoogleSignInUI:**
- `UpdateUI()` - Refresh UI state
- `OnSignInButtonClick()` - Handle sign-in
- `OnSignOutButtonClick()` - Handle sign-out

## 🎯 **Next Steps**

1. **Test the integration** in Unity Editor
2. **Build and test** WebGL version
3. **Deploy to production** environment
4. **Monitor authentication** logs
5. **Implement additional** OAuth scopes as needed

## 📞 **Support**

For issues or questions:
1. Check the **troubleshooting section**
2. Review **Unity console** logs
3. Verify **backend connectivity**
4. Test with **demo scene**

---

**🎉 Happy Coding!**
