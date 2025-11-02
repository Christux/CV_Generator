from generator.app_config import AppConfig
from generator.page_generator import PageGenerator


def test_transform_braces_to_span():

    pg = PageGenerator(app_config=None)

    res = pg._transform_braces_to_span('{red:Python}')

    assert res == r'<span class="red">Python</span>'

def test_transform_braces_to_span_inside_html():

    pg = PageGenerator(app_config=None)

    res = pg._transform_braces_to_span('<strong>{red:Python}</strong>')

    assert res == r'<strong><span class="red">Python</span></strong>'

def test_text_tranformation():

    pg = PageGenerator(app_config=AppConfig())

    data = {
        'content': '- **{red:Python}**'
    }

    data = pg._convert_markdown(data=data)

    assert data['content'] == """<ul>
<li><strong>{red:Python}</strong></li>
</ul>"""

    res = pg._transform_braces_to_span(text=data['content'])

    assert res == """<ul>
<li><strong><span class="red">Python</span></strong></li>
</ul>"""

def test_apply_style_tags():
    pg = PageGenerator(app_config=AppConfig())

    data = {
        'content': '- **{red:Python}**'
    }

    data = pg._convert_markdown(data=data)

    res = pg._apply_style_tags(data=data)

    assert res['content'] == """<ul>
<li><strong><span class="red">Python</span></strong></li>
</ul>"""
