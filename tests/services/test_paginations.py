from src import services


def test_update_page_param_on_url_with_page_param() -> None:
    input_url = "http://api/v1/?page=1"
    result = services.update_page_param(input_url, 1000)
    expected = "http://api/v1/?page=1000"

    assert result == expected


def test_update_page_param_on_url_without_page_param() -> None:
    input_url = "http://api/v1/"
    result = services.update_page_param(input_url, 404)
    expected = "http://api/v1/?page=404"

    assert result == expected


def test_update_page_param_with_other_params() -> None:
    input_url = "http://api/v1/?user=test_user&page=1&size=50"
    result = services.update_page_param(input_url, 1000)
    expected = "http://api/v1/?user=test_user&page=1000&size=50"

    assert result == expected


def test_make_pagination_links_on_first_page() -> None:
    input_page = 1
    input_url = f"http://api/v1/?page={input_page}"
    result = services.make_pagination_links(input_url, 1, 10, 1000)

    assert result.prev is None
    assert result.next == "http://api/v1/?page=2"


def test_make_pagination_links_with_page_greater_than_1() -> None:
    input_page = 10
    input_url = f"http://api/v1/?page={input_page}"
    result = services.make_pagination_links(input_url, 10, 10, 1000)

    assert result.prev == "http://api/v1/?page=9"
    assert result.next == "http://api/v1/?page=11"


def test_make_pagination_links_on_last_page() -> None:
    input_page = 10
    input_url = f"http://api/v1/?page={input_page}"
    result = services.make_pagination_links(input_url, 10, 10, 95)

    assert result.prev == "http://api/v1/?page=9"
    assert result.next is None


def test_make_pagination_links_when_end_equals_total() -> None:
    input_page = 10
    input_url = f"http://api/v1/?page={input_page}"
    result = services.make_pagination_links(input_url, 10, 10, 100)

    assert result.prev == "http://api/v1/?page=9"
    assert result.next is None


def test_make_pagination_links_on_out_of_range_page() -> None:
    input_page = 1000
    input_url = f"http://api/v1/?page={input_page}"
    result = services.make_pagination_links(input_url, 1000, 10, 100)

    assert result.prev == "http://api/v1/?page=999"
    assert result.next is None
