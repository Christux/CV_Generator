from generator.jinja_filters import first_date_filter


def test_date_filter():

    assert first_date_filter("Depuis 2022") == "2022"
    assert first_date_filter("2017-2022") == "2017"
    assert first_date_filter("2014") == "2014"
