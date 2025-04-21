
class WanCmdGenerator:
    TEXT_PROMPT_DICT = {}
    TEXT_PROMPT_DICT["wink_smile"] = "Render a high resolution close up of the person in the image preserving intricate facial textures as he smiles warmly and winks at the camera with a playful tilt and subtle head movement under soft cinematic lighting while the background gently blurs with a smooth depth of field shift and the camera arcs in a seamless slow motion reveal to highlight every expressive detail in fluid motion free of any jitter at high definition."
    TEXT_PROMPT_DICT["Eyebrowraise_nod_smile"] = "Open with a crisp close up that preserves the fine facial details of the person in the image under natural soft light as they raise one eyebrow in a subtle arc then nod gently in affirmation and smile broadly with each gesture flowing seamlessly into the next while the camera drifts slowly to capture a flattering angle with rich saturated colors and smooth transitions that maintain a cinematic and organic feel."
    TEXT_PROMPT_DICT["blowing_kiss_smile"] = "Frame a medium close up with vibrant color grading and realistic skin detail as the person in the image lifts a hand and softly blows a kiss toward the camera with a graceful wrist roll and lip motion captured in smooth slow motion under warm golden hour light while the background blurs elegantly behind a gentle depth of field and the camera dollies in slightly to accentuate the warmth of the gesture in high resolution."
    TEXT_PROMPT_DICT["tilting_head_smile"] = "Begin with a high fidelity shot that captures the fine pores and subtle stubble of the person in the image as they tilt their head gently to one side and break into a genuine smile under diffuse warm lighting while the camera tracks the movement with precise fluidity and the background fades into a soft out of focus glow that flows logically from one frame to the next with rich color depth and no abrupt cuts."
    TEXT_PROMPT_DICT["thumbsup_smile"] = "Show a medium shot highlighting the person in the image from chest up with crisp clarity as they raise a hand in a confident thumbs up and smile broadly under cinematic backlight that casts a gentle rim glow around their form while the camera pans slowly to the right and back to center with rich tones and seamless transitions that keep the energy high and the motion natural."
    TEXT_PROMPT_DICT["heart_hands_smile"] = "Begin with a close up that reveals the detailed texture of the skin and the warmth of the person in the image as they bring both hands together to form a heart shape and beam at the camera under soft diffuse light while the camera slowly zooms out to reveal more of their upper body against a gently blurred backdrop ensuring vivid colors fluid movement and a cohesive cinematic rhythm."
    TEXT_PROMPT_DICT["friendly_wave_smile"] = "Start with a high definition shot capturing the face and shoulders of the person in the image as they raise a hand in a friendly wave and smile openly in warm daylight streaming from stage left while the camera dollies in and out in a gentle arc to follow the motion and the background shifts into a creamy bokeh that enhances natural engagement with rich color depth and smooth storytelling flow."
    TEXT_PROMPT_DICT["oK_hand_smile"] = "Preserving the intricate textures of the skin and facial features the video opens with a dynamic close up of the person smiling and making an OK hand sign under soft natural lighting with a gentle shallow depth of field the camera then smoothly pans out to follow the circular motion of the hand gesture in a fluid arc across a richly colored background creating a vibrant lively scene before settling on a crisp high resolution final frame that maintains organic motion coherence without any jitter or abrupt changes"
    TEXT_PROMPT_DICT["fist_pump_smile"] = "Preserving the realistic detail of the skin and facial features the video begins with an energetic close up capturing the smile as the person pumps their fist upward under warm natural lighting and subtle rim highlights then transitions into a cinematic wide shot that follows the dynamic arm movement in a smooth fluid trajectory enriched by vibrant saturated colors and a gentle depth of field shift the sequence flows seamlessly without abrupt cuts and culminates in a sharp high resolution final frame free of jitter"
    TEXT_PROMPT_DICT["double_thumbs_up_smile"] = "Preserving the fine facial textures the video opens on a tight portrait shot of the person smiling and raising both thumbs up under soft natural lighting with a gentle shallow depth of field the camera then glides smoothly around the subject showcasing the energetic gesture against a backdrop of rich vibrant hues before transitioning to a medium shot that highlights the playful expression the progression feels organic and cinematic throughout and concludes with a pristine high resolution frame that captures every detail without any jitter"
    TEXT_PROMPT_DICT["softly_clapping_smile"] = "Preserving the intricate skin and hand details the video starts with a close up of the person softly clapping and smiling under warm natural lighting that accentuates the gentle contours the camera then gently dollies out while maintaining a shallow depth of field to reveal the rhythmic hand movement in a smooth cinematic flow before transitioning to a medium framing that captures the reflection of soft light on the palms the scene flows naturally with vibrant color tones and ends in a high resolution closing frame free of any jitter"
    TEXT_PROMPT_DICT["finger_guns_smiling"] = "Preserving the realistic skin textures and facial expression the video opens on a crisp close up of the person smiling as they form playful finger guns under soft natural lighting with a subtle shallow depth of field then the camera pivots in a seamless arc following the gesture with fluid motion and dynamic color grading that amplifies the energy before smoothly transitioning to a wider shot the scene maintains organic coherence and ends on a high resolution still free of jitter"
    TEXT_PROMPT_DICT["thumbs_up_leaning_in_smiling"] = "Preserving the fine facial details the video begins with a cinematic close up of the person leaning in with a bright smile and thumbs up under soft natural lighting and a gentle shallow depth of field the camera then smoothly tracks forward enhancing the sense of engagement before transitioning to a medium shot that highlights the vibrant color palette and subtle focus shifts the sequence flows organically without abrupt changes and concludes in a crisp high resolution final frame that retains every texture without any jitter"

    def generate_bash_cmd(self, image_url: str, text_prompts_dict: dict = None) -> str:
        commands = []

        # 1) Generate the UUID once and store it in $unique_id
        commands.append("unique_id=$(uuidgen)")

        # 2) Create your working directory using that variable
        commands.append("mkdir -p i2v_${unique_id}")

        # 3) Download the image once
        commands.append(f"curl -o i2v_${{unique_id}}/image.jpg {image_url}")

        # Use your default prompts if none were passed in
        text_prompts_dict = self.TEXT_PROMPT_DICT if text_prompts_dict is None else text_prompts_dict

        # 4) For each prompt, reference the same $unique_id
        for key, text_prompt in text_prompts_dict.items():
            # Escape any double quotes
            safe_prompt = text_prompt.replace('"', '\\"')
            cmd = (
                f"torchrun --nproc_per_node=4 generate.py "
                f"--task i2v-14B --size \"832*480\" --ckpt_dir ./Wan2.1-I2V-14B-480P "
                f"--image i2v_${{unique_id}}/image.jpg --dit_fsdp --t5_fsdp --ulysses_size 4 "
                f"--save_file i2v_${{unique_id}}/${{unique_id}}_{key}.mp4 "
                f"--prompt \"{safe_prompt}\" && sleep 10"
            )
            commands.append(cmd)

        # Join everything into one paste‑and‑go line
        return " && ".join(commands)

# Example usage
if __name__ == "__main__":
    # Example image URLs and corresponding text prompts
    image_url = "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg"

    # Instantiate the generator and generate the command
    cmd = WanCmdGenerator().generate_bash_cmd(image_url)
    print("Generated Bash Command:")
    print(cmd)


