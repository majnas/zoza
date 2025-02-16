import pytest
from zoza.text_to_image import TextToImage


@pytest.fixture
def mock_meta_ai():
    return TextToImage.from_meta()

def test_text_to_image(mock_meta_ai):
    # Call the __call__ method
    message = """
    Imagine: This image features a heartwarming scene of a baby surrounded by several small birds.
    In the center of the frame is a baby with a bright, joyful smile, showing a few baby teeth. The baby has fair skin, round cheeks, and dark hair. They are wearing a diaper, suggesting a youthful age. The baby is looking directly forward with a very happy and engaged expression. Their arms are outstretched, and they seem to be gently holding or interacting with one of the birds perched on their hand.
    Around the baby are six small, white birds with grey wings and yellow beaks. These birds are perched on different parts of the baby: one is on the baby's head, one is on the baby's left shoulder, one on the right shoulder, one on the left hand, one on the right arm, and one near the baby’s right leg. The birds are all facing different directions, some towards the baby and some away. They appear calm and unafraid, adding to the gentle and peaceful atmosphere of the picture.
    The background is softly blurred, indicating a shallow depth of field which keeps the focus on the baby and the birds. Hints of greenery and out-of-focus pink blossoms suggest an outdoor setting, perhaps a garden or a natural environment. The lighting in the image appears soft and natural, highlighting the baby's and birds' features without harsh shadows.
    Overall, the image conveys a sense of innocence, joy, and harmony between nature and childhood. The baby's happy expression and the presence of the birds create a tender and delightful scene.
    """
    result = mock_meta_ai(message=message)

    # Check if any URL in the response is invalid
    for media in result.get("media", []):
        assert not media["url"].startswith("http"), f"Unexpected valid URL: {media['url']}"
