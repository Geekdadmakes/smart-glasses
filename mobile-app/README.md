# Smart Glasses Mobile App

Flutter companion app for Smart Glasses with cross-platform support (iOS & Android).

## Features

- **Hybrid Bluetooth LE + WiFi Communication**
  - BLE for pairing, setup, and low-bandwidth operations
  - WiFi REST API for high-bandwidth operations (camera, media)
  - Automatic connection switching

- **Complete Smart Glasses Control**
  - Real-time status monitoring (auto-refresh every 5 seconds)
  - Camera viewfinder (snapshot mode)
  - Photo/video gallery with download/delete
  - Full settings control (personality, name, voice, wake word)
  - Full conversation history viewer
  - Voice notes management
  - Todo list with completion tracking
  - Quick actions (photo, video, notes, todos)

- **Settings Management**
  - AI Personality (5 options: friendly, professional, humorous, concise, detailed)
  - AI Name customization
  - Wake word customization
  - Voice engine selection (gtts, pyttsx3, espeak)
  - Voice speed and volume control

- **Media Management**
  - Browse photos and videos
  - Download media to phone
  - Delete unwanted files
  - View metadata (date, size, duration)

## Prerequisites

- Flutter SDK (>= 3.0.0)
- For iOS builds: Xcode 14+ (Mac only)
- For Android builds: Android Studio

## Installation

1. **Install Flutter**
   - Download from https://flutter.dev/docs/get-started/install
   - Add Flutter to your PATH

2. **Verify Installation**
   ```bash
   flutter doctor
   ```

3. **Get Dependencies**
   ```bash
   cd mobile-app
   flutter pub get
   ```

## Running the App

### Android

```bash
flutter run
```

### iOS (Mac only)

```bash
flutter run -d iphone
```

### Build for Release

**Android APK:**
```bash
flutter build apk --release
```

**iOS (requires Mac):**
```bash
flutter build ios --release
```

## Building iOS on Windows (via GitHub Actions)

Since you're developing on Windows, you can use GitHub Actions to build iOS apps:

1. Create `.github/workflows/ios-build.yml`:

```yaml
name: Build iOS

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.16.0'
      - run: flutter pub get
        working-directory: mobile-app
      - run: flutter build ios --release --no-codesign
        working-directory: mobile-app
      - uses: actions/upload-artifact@v3
        with:
          name: ios-build
          path: mobile-app/build/ios/iphoneos/Runner.app
```

2. Push to GitHub and download the build artifact

## Project Structure

```
mobile-app/
├── lib/
│   ├── main.dart                  # App entry point
│   ├── models/                    # Data models
│   │   ├── status.dart
│   │   ├── photo.dart
│   │   ├── video.dart
│   │   ├── note.dart
│   │   ├── todo.dart
│   │   ├── conversation.dart
│   │   └── settings.dart
│   ├── services/                  # Core services
│   │   ├── bluetooth_manager.dart # BLE communication
│   │   ├── api_client.dart        # REST API client
│   │   └── connection_manager.dart # Hybrid connection
│   ├── screens/                   # UI screens
│   │   ├── setup/
│   │   │   └── setup_screen.dart  # Pairing flow
│   │   ├── main_screen.dart       # Tab navigation
│   │   ├── dashboard/
│   │   │   └── dashboard_screen.dart
│   │   ├── camera/
│   │   │   └── camera_screen.dart
│   │   ├── gallery/
│   │   │   └── gallery_screen.dart
│   │   ├── settings/
│   │   │   └── settings_screen.dart
│   │   ├── productivity/
│   │   │   ├── notes_screen.dart  # Voice notes
│   │   │   └── todos_screen.dart  # Todo list
│   │   └── conversation/
│   │       └── conversation_history_screen.dart
│   └── utils/
│       └── app_preferences.dart   # Persistent storage
├── pubspec.yaml                   # Dependencies
└── README.md
```

## Pairing Process

1. **Turn on Smart Glasses**
   - Ensure Bluetooth and WiFi are enabled

2. **Open Mobile App**
   - First launch shows setup screen

3. **Scan for Devices**
   - Tap "Scan for Devices"
   - Select your Smart Glasses from the list

4. **Enter Pairing Code**
   - Smart Glasses will speak a 6-digit code
   - Enter code in app

5. **WiFi Setup (Optional)**
   - Enter WiFi credentials to enable high-bandwidth features
   - Or skip to use Bluetooth only

6. **Done!**
   - App saves pairing and connects automatically

## Dependencies

- **flutter_blue_plus** (^1.32.0) - Bluetooth LE
- **http** (^1.2.0) - REST API client
- **provider** (^6.1.1) - State management
- **shared_preferences** (^2.2.2) - Local storage
- **flutter_secure_storage** (^9.0.0) - Secure storage
- **intl** (^0.19.0) - Date formatting
- **permission_handler** (^11.2.0) - Runtime permissions

## Troubleshooting

### Bluetooth Issues

**Can't find devices:**
- Check Bluetooth is enabled on phone
- Ensure Smart Glasses are powered on
- Try restarting Bluetooth

**Connection fails:**
- Forget device and re-pair
- Check Smart Glasses are not paired with another device

### WiFi Issues

**Can't connect via WiFi:**
- Ensure Smart Glasses are connected to same WiFi network
- Check IP address in connection settings
- Verify API key is correct

**Camera not working:**
- WiFi connection required for camera features
- Check network connectivity
- Try refreshing connection

### Build Issues

**iOS build fails:**
- Ensure Xcode is installed (Mac only)
- Run `pod install` in ios/ directory
- Check code signing settings

**Android build fails:**
- Update Android SDK
- Check gradle version
- Run `flutter clean` then rebuild

## Development

### Running Tests

```bash
flutter test
```

### Code Generation (if needed)

```bash
flutter pub run build_runner build
```

### Formatting

```bash
flutter format lib/
```

## API Reference

See `docs/IOS_APP_GUIDE.md` in the parent directory for complete API documentation.

## License

Part of the Smart Glasses project.
