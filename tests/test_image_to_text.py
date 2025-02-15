import pytest
from zoza.image_to_text import ImageToText

@pytest.fixture
def image_analyzer():
    # model="google/gemini-2.0-flash-thinking-exp:free"
    # model="qwen/qwen-vl-plus:free"
    # model="qwen/qwen2.5-vl-72b-instruct:free"
    model = "qwen/qwen-vl-plus:free"
    return ImageToText(model)

def test_analyze_image(image_analyzer):
    # image_url = "https://static.boredpanda.com/blog/wp-content/uploads/2019/06/funny-cars-46-5cff8f9f19fb3__700.jpg"
    # image_url = "https://static.boredpanda.com/blog/wp-content/uploads/2019/06/funny-cars-185-5d021a50823d6__700.jpg"
    # image_url = "https://static.boredpanda.com/blog/wp-content/uploads/2019/06/funny-cars-43-5cff8efad895f__700.jpg"
    # image_url = "https://static.boredpanda.com/blog/wp-content/uploads/2019/06/funny-cars-152-5d020a1ad47e2__700.jpg"
    # image_url = "https://raw.githubusercontent.com/majnas/Machine_Learning_With_Code/refs/heads/master/Hidden_Markov_Model/data/square_pred.png"
    # image_url = "https://raw.githubusercontent.com/majnas/yolov5_opencv_cpp_python/refs/heads/master/data/me_py_pred.png"
    image_url = "https://github.com/majnas/zoza/blob/master/zoza/asset/baby_and_birds.jpg?raw=true"

    response = image_analyzer.analyze_image(image_url)
    assert isinstance(response, str)
    assert len(response) > 0
