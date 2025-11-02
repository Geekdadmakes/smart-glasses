# Mobile App Testing Checklist

Use this checklist to verify all features are working correctly.

## ✅ Pre-Testing Setup

- [ ] Backend server is running on Raspberry Pi
- [ ] Raspberry Pi is powered on with battery charged
- [ ] Bluetooth is enabled on smart glasses
- [ ] WiFi is configured on smart glasses (optional)
- [ ] Mobile phone has Bluetooth enabled
- [ ] Mobile phone is connected to WiFi (for WiFi mode)
- [ ] App dependencies installed (`flutter pub get`)

## 📱 Initial Setup & Pairing

### First Launch
- [ ] App opens to Setup Screen (not Dashboard)
- [ ] Setup screen shows 3-step wizard

### Step 1: Device Discovery
- [ ] "Scan for Devices" button works
- [ ] Scanning indicator appears
- [ ] Smart Glasses appear in device list
- [ ] Device name shows correctly
- [ ] Can select device from list
- [ ] Connection to device succeeds

### Step 2: Pairing Code
- [ ] Pairing code field appears
- [ ] Can enter 6-digit code
- [ ] Smart glasses speak pairing code
- [ ] Code verification succeeds
- [ ] Invalid code shows error
- [ ] Can go back to device list

### Step 3: WiFi Setup
- [ ] WiFi credential fields appear
- [ ] Can enter SSID
- [ ] Can enter password (obscured)
- [ ] "Skip WiFi" button works
- [ ] Credentials send successfully
- [ ] App navigates to Dashboard after completion

### Pairing Persistence
- [ ] Close and reopen app
- [ ] App goes directly to Dashboard (skip setup)
- [ ] Connection restored automatically

## 🏠 Dashboard Screen

### Status Card
- [ ] Connection status shows "Connected"
- [ ] AI name displays correctly
- [ ] Personality shows correctly
- [ ] Mode shows "Active" or "Sleep"
- [ ] Battery percentage displays
- [ ] Green auto-refresh indicator visible
- [ ] Status updates every 5 seconds

### Sleep/Wake Toggle
- [ ] "Sleep" button puts glasses to sleep
- [ ] Mode changes to "Sleep"
- [ ] "Wake Up" button wakes glasses
- [ ] Mode changes to "Active"

### Quick Actions
- [ ] Photo button captures photo
- [ ] Video button shows duration picker
- [ ] Video recording starts
- [ ] Notes button navigates to Notes screen
- [ ] Todos button navigates to Todos screen

### Recent Conversation
- [ ] Shows last 5 messages
- [ ] Messages display in correct order
- [ ] User messages align right (blue)
- [ ] Assistant messages align left (gray)
- [ ] "View All" button navigates to full history
- [ ] Shows "No recent conversations" when empty

### Real-Time Updates
- [ ] Pull down to refresh works
- [ ] Manual refresh button works
- [ ] Status auto-updates every 5 seconds
- [ ] New messages appear automatically
- [ ] Battery level updates

## 📷 Camera Screen

### Viewfinder
- [ ] Shows placeholder initially
- [ ] Refresh button gets snapshot
- [ ] Snapshot displays correctly
- [ ] Loading indicator shows during fetch
- [ ] Error message if connection fails

### Camera Controls
- [ ] Rotate button rotates image 90°
- [ ] Multiple rotations work (0°, 90°, 180°, 270°)
- [ ] Flip button mirrors image horizontally
- [ ] Flip toggles on/off correctly
- [ ] Controls update viewfinder

### Capture Actions
- [ ] Photo button captures image
- [ ] Success message appears
- [ ] Video button shows duration dialog
- [ ] Duration slider works (5-60 seconds)
- [ ] Video recording starts
- [ ] Recording confirmation shown

## 🖼️ Gallery Screen

### Photos Tab
- [ ] Tab shows photo count
- [ ] Photos display in grid (3 columns)
- [ ] Photos sorted by date (newest first)
- [ ] Timestamp shows on each photo
- [ ] Tap photo shows details dialog
- [ ] Shows "No photos yet" when empty

### Photo Details Dialog
- [ ] Filename displays
- [ ] Date/time displays
- [ ] File size displays
- [ ] Download button works
- [ ] Delete button shows confirmation
- [ ] Deleting removes photo

### Videos Tab
- [ ] Tab shows video count
- [ ] Videos display in list
- [ ] Each video shows:
  - [ ] Filename
  - [ ] Timestamp
  - [ ] Duration
  - [ ] File size
- [ ] Menu button (3 dots) appears
- [ ] Shows "No videos yet" when empty

### Video Actions
- [ ] Download option in menu
- [ ] Download saves to phone
- [ ] Delete option in menu
- [ ] Delete shows confirmation
- [ ] Deleting removes video

### Gallery Features
- [ ] Pull to refresh reloads media
- [ ] Refresh button works
- [ ] Error handling for connection issues

## ⚙️ Settings Screen

### AI Settings Section
- [ ] Personality tile shows current value
- [ ] Tap opens personality dialog
- [ ] Can select from 5 options:
  - [ ] Friendly
  - [ ] Professional
  - [ ] Humorous
  - [ ] Concise
  - [ ] Detailed
- [ ] Personality updates successfully
- [ ] Success message appears

### Name Setting
- [ ] Name tile shows current AI name
- [ ] Tap opens edit dialog
- [ ] Can enter new name
- [ ] Save button updates name
- [ ] Cancel button discards changes

### Wake Word Setting
- [ ] Wake word tile shows current value
- [ ] Tap opens edit dialog
- [ ] Can enter new wake word
- [ ] Save button updates wake word
- [ ] Success message appears

### Voice Settings Section
- [ ] Voice engine shows current value
- [ ] Tap opens engine selection dialog
- [ ] Can select from 3 engines:
  - [ ] GTTS
  - [ ] PYTTSX3
  - [ ] ESPEAK
- [ ] Engine updates successfully

### Voice Speed
- [ ] Slider shows current rate
- [ ] Can drag slider (50-300)
- [ ] Label shows current value
- [ ] Updates in real-time
- [ ] Changes saved to glasses

### Voice Volume
- [ ] Slider shows current volume
- [ ] Can drag slider (0-100%)
- [ ] Label shows percentage
- [ ] Updates in real-time
- [ ] Changes saved to glasses

### Connection Info
- [ ] Shows connection status
- [ ] Shows connection type (Bluetooth/WiFi)
- [ ] Green check when connected
- [ ] Red X when disconnected

### Device Management
- [ ] "Unpair Device" button visible
- [ ] Tap shows confirmation dialog
- [ ] Confirming unpairs device
- [ ] App returns to Setup screen
- [ ] All saved data cleared

## 📝 Notes Screen

### Notes List
- [ ] Shows all voice notes
- [ ] Notes sorted by date (newest first)
- [ ] Each note shows:
  - [ ] Content preview (2 lines max)
  - [ ] Timestamp
- [ ] Shows "No notes yet" when empty
- [ ] Pull to refresh works

### Add Note
- [ ] Tap + button opens dialog
- [ ] Can enter note text
- [ ] Add button saves note
- [ ] Cancel button discards
- [ ] Success message appears
- [ ] New note appears in list

### View Note
- [ ] Tap note opens detail dialog
- [ ] Full content displays
- [ ] Timestamp displays
- [ ] Close button works

### Delete Note
- [ ] Delete button (trash icon) on note
- [ ] Shows confirmation dialog
- [ ] Confirming deletes note
- [ ] Note removed from list
- [ ] Success message appears

## ✅ Todos Screen

### Todo List
- [ ] Shows all tasks
- [ ] Separated into sections:
  - [ ] Pending tasks
  - [ ] Completed tasks
- [ ] Each todo shows:
  - [ ] Checkbox
  - [ ] Task text
  - [ ] Timestamp
- [ ] Shows "No todos yet" when empty
- [ ] Section headers show counts

### Add Todo
- [ ] Tap + button opens dialog
- [ ] Can enter task text
- [ ] Add button saves todo
- [ ] Cancel button discards
- [ ] New todo appears in Pending

### Toggle Todo
- [ ] Tap checkbox toggles completion
- [ ] Completed todos move to Completed section
- [ ] Completed todos show strikethrough
- [ ] Completed todos grayed out
- [ ] Unchecking moves back to Pending

### Delete Todo
- [ ] Delete button (trash icon) appears
- [ ] Deleting removes todo
- [ ] Works for both pending and completed
- [ ] Success message appears

## 💬 Conversation History Screen

### Message Display
- [ ] All messages display
- [ ] User messages:
  - [ ] Align right
  - [ ] Blue background
  - [ ] Rounded corners
- [ ] Assistant messages:
  - [ ] Align left
  - [ ] Gray background
  - [ ] Rounded corners
- [ ] Each message shows timestamp
- [ ] Messages in chronological order

### Timestamps
- [ ] Today shows time only
- [ ] Yesterday shows "Yesterday + time"
- [ ] This week shows day name + time
- [ ] Older shows full date + time

### Actions
- [ ] Pull to refresh reloads
- [ ] Refresh button in app bar
- [ ] Clear history button appears when messages exist
- [ ] Clear shows confirmation dialog
- [ ] Confirming clears all messages
- [ ] Shows "No conversation history" when empty

## 🔄 Navigation & App Behavior

### Bottom Navigation
- [ ] Dashboard tab selected by default
- [ ] Camera tab switches to camera screen
- [ ] Gallery tab switches to gallery screen
- [ ] Settings tab switches to settings screen
- [ ] Selected tab highlighted
- [ ] Tab icons change (outlined/filled)

### Back Navigation
- [ ] Back button on sub-screens returns to previous
- [ ] Notes screen back goes to Dashboard
- [ ] Todos screen back goes to Dashboard
- [ ] Conversation screen back goes to Dashboard
- [ ] Android back button works
- [ ] iOS swipe back works

### App State
- [ ] App remembers last tab
- [ ] Closing and reopening preserves connection
- [ ] Background and foreground works
- [ ] Polling stops when backgrounded
- [ ] Polling resumes when foregrounded

## 🎨 UI/UX

### Visual Design
- [ ] Material Design 3 components used
- [ ] Consistent color scheme
- [ ] Proper spacing and padding
- [ ] Icons are clear and meaningful
- [ ] Text is readable

### Dark Mode
- [ ] App respects system theme
- [ ] Switch to dark mode works
- [ ] All screens readable in dark mode
- [ ] Colors adjust appropriately
- [ ] No white flashes

### Loading States
- [ ] Circular progress indicators show
- [ ] Loading doesn't block UI unnecessarily
- [ ] Silent loading during auto-refresh
- [ ] Manual refresh shows loading

### Error States
- [ ] Error messages are clear
- [ ] Error icon displays
- [ ] Retry button available
- [ ] Errors don't crash app

### Empty States
- [ ] Friendly empty messages
- [ ] Icons for empty states
- [ ] Helpful instructions
- [ ] Call-to-action visible

## 🔌 Connection Scenarios

### Bluetooth Only
- [ ] Can pair and connect
- [ ] All features work via BLE
- [ ] Camera uses BLE (slower)
- [ ] Settings update via BLE

### WiFi Only (after pairing)
- [ ] Can connect via WiFi
- [ ] Camera is faster
- [ ] Media downloads faster
- [ ] All REST API calls work

### Hybrid Mode
- [ ] App uses WiFi when available
- [ ] Falls back to BLE when WiFi unavailable
- [ ] Connection status shows current type
- [ ] Seamless switching

### Disconnection Recovery
- [ ] App detects disconnection
- [ ] Error messages appear
- [ ] Can manually reconnect
- [ ] Auto-reconnect attempts

## 🐛 Edge Cases

### Network Issues
- [ ] Handles slow connections
- [ ] Timeout errors shown
- [ ] Retry mechanism works
- [ ] Doesn't freeze on network error

### Invalid Data
- [ ] Handles missing fields gracefully
- [ ] Null values don't crash app
- [ ] Invalid JSON handled
- [ ] Malformed data shown as error

### Permissions
- [ ] Bluetooth permission requested (Android)
- [ ] Location permission requested (Android BLE)
- [ ] Permission denial handled gracefully
- [ ] Settings redirect works

### Low Battery
- [ ] Battery level displays correctly
- [ ] Low battery warning (if implemented)
- [ ] App continues to work

## 📊 Performance

### Responsiveness
- [ ] UI doesn't lag
- [ ] Animations smooth
- [ ] No jank during scrolling
- [ ] Button taps respond immediately

### Memory
- [ ] No memory leaks during normal use
- [ ] App doesn't grow in memory over time
- [ ] Images released after viewing

### Battery
- [ ] Polling doesn't drain battery excessively
- [ ] BLE connection efficient
- [ ] App backgrounded saves battery

## ✨ Polish

### Feedback
- [ ] All actions show feedback
- [ ] Success snackbars appear
- [ ] Error snackbars appear
- [ ] Loading indicators present

### Confirmations
- [ ] Destructive actions require confirmation
- [ ] Delete dialogs work
- [ ] Unpair requires confirmation
- [ ] Clear history requires confirmation

### Accessibility
- [ ] Text is readable
- [ ] Touch targets large enough
- [ ] Color contrast sufficient
- [ ] Screen reader friendly (bonus)

---

## 📝 Testing Notes

**Date Tested:** ________________

**Tester:** ________________

**Device:** ________________

**OS Version:** ________________

**Issues Found:**
```
1.
2.
3.
```

**Overall Status:** ☐ Pass  ☐ Fail  ☐ Needs Work

**Notes:**
```



```
