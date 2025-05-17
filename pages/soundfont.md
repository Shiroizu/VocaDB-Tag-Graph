---
url: https://vocadb.net/T/9177
name: SoundFont
additionalNames: 
- SF2
parent: "[[parentless]]"
related:
- "[[dtm]]"
mappedNicoTags:

newTargets:
- all
commentCount: 2
createDate: 2022-10-16T00:00:07.027
status: Finished
albumCount: 3
artistCount: 4
eventCount: 0
eventSeriesCount: 0
followerCount: 2
songListCount: 0
songCount: 25
links: 

picture: false
descriptionLength: 2748
---

#Sources

SoundFont is a brand name that collectively refers to a file format and associated technology that uses sample-based synthesis to play MIDI files. SoundFonts contain audio recording samples that can be mapped out on a virtual keyboard as an instrument, a sound effect, a percussion kit, etc. For example, an orchestral SoundFont can contain a single Violin, a string section, a percussion set, and a choir that can only say the word "Ah" and "Ooh."

There are multiple ways an instrument in a SoundFont can be mapped on a virtual keyboard to play MIDI files. The organization of a SoundFont is set into categories of audio samples and those categories are commonly called "instruments" since those are the types of audio samples SoundFonts most commonly use. An instrument in a SoundFont can contain one or multiple audio recordings of a real instrument at different pitches. Those recordings can either change pitch relative to the note being played on the keyboard or it can be set to only play a recording at a specific note on a keyboard regardless of what pitch the audio is set to. They can also contain music synthesis parameters such as vibrato, looping, and velocity-sensitive volume changes.

Multiple instruments in one SoundFont cannot be played on one MIDI track because MIDI tracks can only use one instrument at a time. This is because MIDI files can tell what notes are being played and what parameters are being used by the software hosting the SoundFont, but they cannot distinguish lyrics, what instruments are being used and whether or not there are different techniques being used. For example, a choir SoundFont can have an instrument that contains multiple sound recordings of a choir saying the word "ah." However, if there are recordings of a choir singing different words in one instrument, then the range those words can be sung will be limited because a virtual keyboard cannot switch between what word is being played on a specific note. Therefore, it would be necessary to make separate instruments for specific words. This makes using SoundFonts to host a complex instrument like the human voice VERY impractical and thus is usually limited to only producing "Ahs" and "Oohs."

SoundFonts function most similarly to an UTAU Voicebank that is recorded in the CV format. They both use audio recordings, those audio recordings can be set at specific pitches and those audio recordings can change to other pitches using pitch and formant plugins. SoundFonts also contain parameters that are similar to "otoing" the audio files of a CV voicebank. However, the biggest difference between those two is that UTAU Voicebanks can change what audio sample is being used in a UST while SoundFonts cannot do that with a MIDI file.

---

