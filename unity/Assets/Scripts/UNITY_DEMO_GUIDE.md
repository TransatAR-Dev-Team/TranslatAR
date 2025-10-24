# 🚀 Unity Google Sign-In Demo - Step by Step Guide

## ✅ **Backend Status: RUNNING**
Your TranslatAR backend is running and ready at `http://localhost:8000`

## 🎮 **Unity Setup Instructions:**

### **Step 1: Open Unity Project**
1. Open Unity Editor
2. Open the project located at: `/Users/wei-lun/Desktop/TranslatAR-Google-oauth/unity/`

### **Step 2: Create Demo Scene**
1. Create a new scene: `File → New Scene`
2. Save it as: `GoogleSignInDemo.unity`

### **Step 3: Setup UI Canvas**
1. Right-click in Hierarchy → `UI → Canvas`
2. Set Canvas Scaler to "Scale With Screen Size"
3. Add the following UI elements:

#### **Login Panel:**
- Right-click Canvas → `UI → Panel` (name it "LoginPanel")
- Add `UI → Button` (name it "SignInButton")
- Add `UI → Text - TextMeshPro` (name it "StatusText")

#### **User Panel:**
- Right-click Canvas → `UI → Panel` (name it "UserPanel")
- Add `UI → Image` (name it "UserProfileImage")
- Add `UI → Text - TextMeshPro` (name it "UserInfoText")
- Add `UI → Button` (name it "SignOutButton")

### **Step 4: Add Scripts to Scene**
1. Create empty GameObject (name it "GoogleSignInManager")
2. Add `GoogleSignInManager` component to it
3. Add `UnityGoogleSignInDemo` component to it

### **Step 5: Configure Components**

#### **GoogleSignInManager:**
- **Client ID**: `861587845879-v6ih92nnkk9h1isaiv7gafaqaguockq8.apps.googleusercontent.com`
- **Redirect URI**: `http://localhost:8000/auth/google/callback`
- **Backend URL**: `http://localhost:8000`

#### **UnityGoogleSignInDemo:**
- **Sign In Button**: Drag the SignInButton from hierarchy
- **Sign Out Button**: Drag the SignOutButton from hierarchy
- **Status Text**: Drag the StatusText from hierarchy
- **User Info Text**: Drag the UserInfoText from hierarchy
- **User Profile Image**: Drag the UserProfileImage from hierarchy

### **Step 6: Test the Login**

#### **Method 1: Play Mode Testing**
1. Click the **Play** button in Unity
2. Click the **"Sign In with Google"** button
3. Your browser will open with Google OAuth
4. Complete the Google sign-in process
5. Return to Unity to see the user profile

#### **Method 2: Build and Run**
1. `File → Build Settings`
2. Select your target platform
3. Click **Build and Run**
4. Test the Google Sign-In in the built application

## 🔧 **Troubleshooting:**

### **If "GoogleSignInManager not found":**
- Make sure you added the `GoogleSignInManager` component to a GameObject in the scene
- The component should be on a GameObject that persists across scenes

### **If "Backend connection failed":**
- Ensure your backend is running: `docker compose up -d`
- Check the backend URL in the GoogleSignInManager component

### **If "OAuth popup blocked":**
- Allow popups in your browser
- The system will fall back to same-window redirect

## 📱 **Expected Behavior:**

### **Before Sign-In:**
- Shows "Sign In with Google" button
- Status text shows "User is not signed in"

### **During Sign-In:**
- Button click opens browser with Google OAuth
- Status text shows "Starting Google Sign-In process..."
- User completes Google authentication in browser

### **After Sign-In:**
- Shows user profile with name, email, and profile picture
- Shows "Sign Out" button
- Status text shows "User signed in successfully!"

## 🎯 **Quick Test Commands:**

### **In Unity Console:**
```csharp
// Check authentication status
GoogleSignInManager.Instance.IsAuthenticated()

// Get current user
GoogleSignInManager.Instance.GetCurrentUser()

// Get auth token
GoogleSignInManager.Instance.GetAuthToken()
```

### **Backend API Test:**
```bash
# Test OAuth endpoint
curl http://localhost:8000/auth/google

# Test token verification
curl "http://localhost:8000/auth/verify?token=test"
```

## 🚀 **Ready to Test!**

Your Unity Google Sign-In is now ready to test! Follow the steps above to set up the demo scene and start testing the authentication flow.

**The system will:**
1. ✅ Open Google OAuth in your browser
2. ✅ Handle the authentication flow
3. ✅ Return user profile to Unity
4. ✅ Display user information in the UI
5. ✅ Manage authentication state

**🎉 Happy Testing!**