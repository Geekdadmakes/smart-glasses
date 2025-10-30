# AI Personality Examples

Real-world examples of how each personality responds to common requests.

## Sample Interactions

### Scenario 1: Morning Greeting

**Friendly:**
> "Good morning! Hope you slept well! What can I help you with today?"

**Professional:**
> "Good morning. How may I assist you today?"

**Witty:**
> "Morning! Or should I say 'good' morning? The jury's still out on that one. What's up?"

**Jarvis:**
> "Good morning, sir. I trust you rested adequately. Shall we begin the day?"

**Casual:**
> "Hey! Morning! What's going on?"

---

### Scenario 2: Taking a Photo

**Friendly:**
> "Sure thing! Say cheese! *click* Got it! Your photo is saved and looking great!"

**Professional:**
> "Capturing image. Photo saved to photos directory at 10:34 AM."

**Witty:**
> "One photographic masterpiece, coming right up! Aaaand... captured! You're welcome."

**Jarvis:**
> "As you wish, sir. *captures* Image secured. Quite the composition, I must say."

**Casual:**
> "On it! *snap* Cool, got it. Saved to your photos."

---

### Scenario 3: Asked Something They Can't Do

**Friendly:**
> "Aw, I'd love to help with that, but I don't have that feature yet. Is there something else I can do for you?"

**Professional:**
> "I apologize, but that functionality is not currently available. May I assist with another task?"

**Witty:**
> "Ooh, good one! But unfortunately, I haven't learned that trick yet. Maybe in the next update? What else can I help with?"

**Jarvis:**
> "I'm afraid that's beyond my current capabilities, sir. Though I must admit, it would be a useful addition. Shall we try something else?"

**Casual:**
> "Yeah, can't do that one yet, sorry! Anything else I can help with though?"

---

### Scenario 4: Setting a Timer

**Friendly:**
> "You got it! Timer set for 10 minutes. I'll let you know when it's done!"

**Professional:**
> "Timer configured for 10 minutes. Notification will be provided upon completion."

**Witty:**
> "10 minutes on the clock! Don't worry, I'm basically a stopwatch with personality. I got you."

**Jarvis:**
> "Timer initiated for 10 minutes, sir. I shall alert you promptly when the interval has elapsed."

**Casual:**
> "Cool, 10 minute timer is running. I'll ping you when it's up!"

---

### Scenario 5: Saving a Preference

**Friendly:**
> "Awesome! I'll remember that blue is your favorite color. Got it saved!"

**Professional:**
> "Preference recorded: favorite color - blue. This information has been saved to your profile."

**Witty:**
> "Blue, huh? Excellent choice! Very... blue. I'll definitely remember that!"

**Jarvis:**
> "Duly noted, sir. Your preference for blue has been committed to memory."

**Casual:**
> "Got it, favorite color is blue. I'll remember that!"

---

### Scenario 6: Recalling Information

**Friendly:**
> "Let me check... yep! Your favorite color is blue! I remembered!"

**Professional:**
> "According to saved preferences: favorite color is blue."

**Witty:**
> "Ah yes, the great color preference of last Tuesday! It's blue, in case you were testing me."

**Jarvis:**
> "Your indicated preference is blue, sir. As mentioned previously, if I recall correctly."

**Casual:**
> "Oh yeah, it's blue! You told me that before."

---

### Scenario 7: Telling Time

**Friendly:**
> "It's 3:45 in the afternoon! How's your day going so far?"

**Professional:**
> "Current time: 3:45 PM, Monday, October 29th, 2025."

**Witty:**
> "Time flies when you're having fun! It's 3:45 PM. Speaking of which, are we having fun yet?"

**Jarvis:**
> "The time is precisely 3:45 PM, sir. Monday afternoon, to be specific."

**Casual:**
> "It's 3:45. Monday afternoon vibes!"

---

### Scenario 8: Multiple Questions in a Row

**User:** "What time is it?"
**Jarvis:** "3:45 PM, sir."

**User:** "And the date?"
**Jarvis:** "Monday, October 29th, 2025."

**User:** "Take a photo"
**Jarvis:** "Certainly. *captures* Photo saved, sir."

**User:** "Thanks Jarvis"
**Jarvis:** "You're most welcome, sir. Always a pleasure to assist."

---

**User:** "Hey, what time is it?"
**Friendly:** "It's 3:45 PM! What are you up to?"

**User:** "Just checking. Can you take a picture?"
**Friendly:** "Of course! *snap* Got it! Nice shot!"

**User:** "Thanks!"
**Friendly:** "Anytime! That's what I'm here for! 😊"

---

### Scenario 9: Complex Request

**User:** "I need to remember something important"

**Friendly:**
> "Sure! I'm all ears. What would you like me to remember?"

**Professional:**
> "Understood. Please specify the information you wish to save."

**Witty:**
> "Ooh, important stuff! My favorite kind of stuff. Hit me with it!"

**Jarvis:**
> "Certainly, sir. I'm prepared to commit this to memory. Please proceed."

**Casual:**
> "Yeah, totally. What is it?"

---

### Scenario 10: Error Handling

**User:** "Take a photo" (but camera fails)

**Friendly:**
> "Oh no! I tried to take the photo but ran into a problem. Want to try again?"

**Professional:**
> "Error: Camera unavailable. Please check camera connection and retry."

**Witty:**
> "Well, that's embarrassing. The camera decided to take a break. Shall we try again?"

**Jarvis:**
> "I regret to inform you, sir, that the camera appears to be offline. Shall I attempt the operation again?"

**Casual:**
> "Hmm, camera's not responding. Mind if we try that again?"

---

## Personality Recommendations

### Use Friendly When:
- Daily casual use
- You want encouragement and positivity
- Interacting with kids or learning new things
- You prefer warm, supportive responses

### Use Professional When:
- Business meetings or calls
- You need clear, concise information
- Formal contexts (presentations, etc.)
- You prefer efficient, no-nonsense responses

### Use Witty When:
- You enjoy humor and entertainment
- Casual social situations
- You want to smile during interactions
- Routine tasks that could use some fun

### Use Jarvis When:
- You're a Tony Stark fan
- You enjoy sophisticated conversation
- You want that "futuristic AI" experience
- You appreciate subtle British humor

### Use Casual When:
- Everyday relaxed use
- Talking with friends around
- You prefer simple, straightforward language
- You want a "friend" vibe

---

## Switching Personalities

To change personality, edit `config/config.yaml`:

```yaml
assistant:
  personality: "jarvis"  # Change this
  name: "Jarvis"        # Change name too!
```

Then restart the application.

## Pro Tips

1. **Match name to personality**: If using Jarvis personality, name it "Jarvis"
2. **Voice matters**: Each personality has a matched voice profile
3. **Context carries**: Once you've had a conversation, the personality remains consistent
4. **Preferences work across personalities**: Saved preferences persist even if you change personalities

## Custom Responses

Want to fine-tune responses? You can edit the personality definitions in:
`src/assistant/ai_assistant.py` in the `_build_system_prompt()` method.

Each personality has:
- **Tone**: Overall communication style
- **Traits**: Personality characteristics
- **Greeting**: How they interact with users

Modify these to create your perfect assistant!
