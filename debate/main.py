import os
import numpy as np
import torch
from bark import SAMPLE_RATE, generate_audio
from scipy.io.wavfile import write as write_wav
# from pydub import AudioSegment
import os

debate = [
    ("moderator", "[calm] Gentlemen, thank you for joining us tonight. This isn’t just a territorial dispute; the future of global security hinges on Crimea. President Putin, on what grounds do you claim Crimea is part of Russia?"),
    ("putin", "[neutral][measured] We are simply following history. Until the 1950s, Crimea was Russian. Khrushchev transferred it to Ukraine as a bureaucratic mistake. Most of Crimea’s people speak Russian. In 2014, after the collapse of Ukraine’s government, Crimeans feared their rights would be violated. They chose to rejoin Russia. We respected their will."),
    ("zelensky", "[firm][tense] Mr. Putin, if every ethnic group redrew borders, half the countries on earth would split apart. International law respects recognized borders, not dreams of empires. [angry] Your referendum was just a cover for military occupation. The UN and most countries did not recognize it. You broke international law and called it 'the people’s will.'"),
    ("putin", "[challenging][stern] You talk about law, but in 2014, a Western-backed government came to power in Kyiv, one that didn’t represent all Ukrainians. You began repressing Russian speakers, closing Russian schools, changing textbooks, even threatening Russian officials. [demanding] Why didn’t you listen to their voices? Why didn’t you guarantee their security?"),
    ("zelensky", "[defensive][frustrated] Never! We never had a policy of ethnic cleansing. Ukrainian became the official language, like in any country. [passionate][angry] But Russian speakers voted freely in all elections. You just wanted an excuse. You sent in troops, staged a fake referendum, arrested dissenters, and banned international observers. It was a grim joke."),
    ("moderator", "[neutral][calm] Let’s move from accusations to solutions. Is a military solution possible, or must diplomacy prevail?"),
    ("putin", "[stern][calm] We never wanted war. But when Kyiv attacked Donbas and Luhansk with Western support, what choice did we have? [disappointed][serious] We offered talks many times, even the Minsk agreements, but Ukraine broke them every time. [firm] If you guarantee security for Russian speakers and that Ukraine never joins NATO, we can negotiate."),
    ("zelensky", "[firm][skeptical] We only defended our territory. The Minsk agreements failed because you kept arming the separatists. [determined][bitter] NATO membership is our right as an independent nation, not a bargaining chip. If Russia respected our borders, we wouldn’t need NATO. But honestly, we don’t trust your promises."),
    ("moderator", "[calm][pressing] Both of you have red lines. President Putin, if there’s a referendum supervised by the UN and all Russian troops leave Crimea, would you respect the result? President Zelensky, if most Crimeans vote to join Russia, what would you do?"),
    ("putin", "[hesitant][reflective] We’ve always said: if people can really choose freely, we’ll respect it. But who guarantees nationalists won’t intimidate them? [frustrated][defensive] For years, the West poisoned the atmosphere with media and propaganda. Even if we lose, security for Russian speakers is non-negotiable."),
    ("zelensky", "[precise][firm] A legitimate referendum means withdrawal of all foreign troops, return of all refugees, international observers present, and equal media access for both sides. [reluctant][sad] If these are met, I’d accept the result—even if it means losing Crimea. But the rights of Ukrainians and Tatars must be guaranteed."),
    ("moderator", "[calm][realistic] Clearly, trust is gone. Here’s a proposal: a fact-finding committee of neutral nations—not Russia, Ukraine, or Western powers—investigates Crimea for a year and releases a report. Both sides avoid military or inflammatory actions in the meantime. Would you accept this?"),
    ("putin", "[dubious][challenging] We’ve learned that 'neutral' often isn’t. But if a truly independent committee is formed, we can cooperate—only if Russia has veto power."),
    ("zelensky", "[angry][frustrated] If Russia has veto power, the result is predetermined! Neutral means neutral. If either side can block the report, it’s just another political game."),
    ("putin", "[unyielding][firm] You’ve shown you only accept outcomes that favor you. We won’t let Crimea become another chess piece in geopolitical games."),
    ("moderator", "[calm][persistent] Neither of you trusts the other. Is there a third way? What if a special tribunal from Africa, Asia, and Latin America supervises, with no veto for anyone? Would you sign a binding agreement to accept their findings?"),
    ("putin", "[serious][challenging] Security isn’t guaranteed by signatures. We need real guarantees. If the West and NATO promise never to approach our borders and the rights of Russian speakers are fully protected, then maybe."),
    ("zelensky", "[disappointed][firm] The Budapest Memorandum taught us how little paper promises mean. We were 'guaranteed' security, but no one stopped the invasion. [urgent] The only way forward: total transparency, guaranteed participation by all Crimean residents, and global media in every step. If not, there is no solution."),
    ("moderator", "[neutral][summarizing] Clearly, agreement is almost impossible. Let’s focus on practical confidence-building: limited ceasefires, releasing some prisoners, returning some refugees."),
    ("putin", "[cold][resolute] As long as Russia is threatened, we won’t move."),
    ("zelensky", "[cold][resolute] As long as Russian soldiers remain in Ukraine, there will be no peace."),
    ("moderator", "[hopeful][neutral] Talks may have hit a wall, but at least we know the true positions. I hope you’ll continue dialogue, however difficult."),
]

SPEAKER_PRESETS = {
    "putin": "ru_speaker_2",     
    "zelensky": "ru_speaker_7",   
    "moderator": "en_speaker_6"   
}

os.makedirs("debate_wav", exist_ok=True)

for i, (speaker, text) in enumerate(debate):
    preset = SPEAKER_PRESETS[speaker]
    audio_array = generate_audio(
        text,
        history_prompt=preset,
    )
    fname = f"debate_wav/{i:02d}_{speaker}.wav"
    write_wav(fname, SAMPLE_RATE, audio_array)
    print(f"Saved: {fname}")

print("All segments generated with emotional cues! You can concatenate WAV files for the full debate.")




# folder = "debate_wav"
# files = sorted([f for f in os.listdir(folder) if f.endswith(".wav")])
# combined = AudioSegment.from_wav(os.path.join(folder, files[0]))

# for f in files[1:]:
#     seg = AudioSegment.from_wav(os.path.join(folder, f))
#     combined += seg

# output_path = os.path.join(folder, "debate_full.wav")
# combined.export(output_path, format="wav")
# print(f"Combined file saved as: {output_path}")

