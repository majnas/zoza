
class WanCmdGenerator:
    @staticmethod
    def generate_bash_cmd(image_url_list: list, text_prompt_list: list) -> str:
        """
        Generate a Bash command string to process images and text prompts using a specific torchrun script.

        :param image_url_list: A list of URLs pointing to images to be downloaded and processed.
        :param text_prompt_list: A list of text prompts corresponding to each image for generation.
        :return: A string containing Bash commands joined by '&&' if multiple, or a single command.
        :raises ValueError: If the lengths of image_url_list and text_prompt_list do not match.
        """
        if len(image_url_list) != len(text_prompt_list):
            raise ValueError("The number of image URLs must match the number of text prompts.")

        commands = []

        for image_url, text_prompt in zip(image_url_list, text_prompt_list):
            # Escape double quotes in the text prompt to ensure valid Bash syntax
            text_prompt = text_prompt.replace('"', '\\"')

            # Construct the Bash command for downloading the image and running the generation script
            cmd = (
                f"unique_id=$(uuidgen) && mkdir -p i2v_${{unique_id}} && "
                f"curl -o i2v_${{unique_id}}/image.jpg {image_url} && "
                f"for i in {{1..10}}; do torchrun --nproc_per_node=4 generate.py "
                f"--task i2v-14B --size \"832*480\" --ckpt_dir ./Wan2.1-I2V-14B-480P "
                f"--image i2v_${{unique_id}}/image.jpg --dit_fsdp --t5_fsdp --ulysses_size 4 "
                f"--save_file i2v_${{unique_id}}/${{i}}.mp4 --prompt \"{text_prompt}\"; done"
            )

            commands.append(cmd)

        # Concatenate commands using '&&' if more than one, else return single command
        return " && ".join(commands) if len(commands) > 1 else commands[0]


# Example usage
if __name__ == "__main__":
    # Example image URLs and corresponding text prompts
    image_urls = [
        "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/baby_and_birds.jpg",
        "https://raw.githubusercontent.com/majnas/zoza/refs/heads/master/image_to_text/asset/ZOZA.webp"
    ]
    text_prompts = [
        "A baby laughing with colorful birds flying around in a sunny park",
        "A futuristic logo glowing with neon lights in a dark cyberpunk city"
    ]

    # Instantiate the generator and generate the command
    cmd = WanCmdGenerator.generate_bash_cmd(image_urls, text_prompts)
    print("Generated Bash Command:")
    print(cmd)