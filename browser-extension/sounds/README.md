# Alert Sounds

This directory contains sound files for extension notifications.

## Required Files

- `alert.mp3` - Critical alert sound (played for high/critical risk alerts)

## Sound Guidelines

1. **Keep it short** - Under 2 seconds
2. **Use notification-style sounds** - Short, attention-grabbing but not jarring
3. **Low volume** - The sound should be subtle
4. **Royalty-free** - Only use sounds you have rights to

## Free Sound Resources

- https://freesound.org/ (requires free account)
- https://notificationsounds.com/
- https://www.zapsplat.com/

## Recommended Sound Characteristics

- **Type**: Short beep, chime, or gentle alert
- **Duration**: 0.5 - 1.5 seconds
- **Volume**: -12dB to -6dB (not too loud)
- **Format**: MP3 (320kbps or lower for small file size)

## File Size

Keep the MP3 under 50KB for fast loading. Use a lower bitrate if needed:

```bash
# Compress audio with ffmpeg
ffmpeg -i alert-source.mp3 -b:a 96k -ar 22050 alert.mp3
```

## Disabling Sounds

Users can disable sounds in the extension options page under Display settings.
