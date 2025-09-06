import pytest
from sandbox.binance_prep_1 import (
    fetch_order_book_snapshot,
    extract_asks,
    check_sufficient_volume,
    calculate_price,
    InvalidOrderBook,
    InsufficientDepthOrderBook,
    url,
    params
    )

class TestFetchOrderBookSnapshot:
    @pytest.mark.it('fetches the order book')
    def test_return_dict_with_correct_keys(self):
        order_book = fetch_order_book_snapshot(url, params)
        assert isinstance(order_book, dict)
        assert 'asks' in order_book.keys()
        assert 'bids' in order_book.keys()

class TestExtractAsks:
    def test_return_correct_value_for_asks(self):
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '0.64277000'], ['110675.62000000', '0.00010000']]
                    }
        assert extract_asks(order_book) ==  [['110675.59000000', '6.58899000'], ['110675.60000000', '0.64277000'], ['110675.62000000', '0.00010000']] 

    def test_raises_error_if_asks_have_no_value(self):
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': []
                    }
        with pytest.raises(InvalidOrderBook) as e:
            extract_asks(order_book)


class TestCheckSufficientVolume:
    @pytest.mark.it ("Returns True if the depth is sufficient")
    def test_returns_true_sufficient_depth (self):
        purchase_qty = 1
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '0.64277000'], ['110675.62000000', '0.00010000']]
                    }
        order_book_asks = extract_asks(order_book)
        assert check_sufficient_volume(order_book_asks, purchase_qty)

    @pytest.mark.it ("Raises error if the depth is not sufficient")
    def test_raises_error_insufficient_depth (self):
        purchase_qty = 100
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '0.64277000'], ['110675.62000000', '0.00010000']]
                    }
        order_book_asks = extract_asks(order_book)
        with pytest.raises(InsufficientDepthOrderBook):
            check_sufficient_volume(order_book_asks, purchase_qty)

class TestCalculatePrice:
    @pytest.mark.it ('Gives correct result if the best ask is sufficient')
    def test_sufficient_best_ask(self):
        purchase_qty = 5
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '0.64277000'], ['110675.62000000', '0.00010000']]
                    }
        order_book_asks = extract_asks(order_book)
        assert calculate_price(order_book_asks, purchase_qty) == 553377.95

    
    @pytest.mark.it ('Gives correct result if the best ask is not sufficient but there is no fractures')
    def test_insufficient_best_ask_no_fractures(self):
        purchase_qty = 7.58899000
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '1.0000000'], ['110675.62000000', '0.00010000']]
                    }
        order_book_asks = extract_asks(order_book)
        assert calculate_price(order_book_asks, purchase_qty) == 839915.9557541

    @pytest.mark.it ('Gives correct result if the best ask is not sufficient and there are fractures')
    def test_insufficient_best_ask_with_fractures(self):
        purchase_qty = 7.5
        order_book = {'lastUpdateId': 75893573333, 
                        'bids': [['110675.58000000', '0.58772000'], ['110675.57000000', '0.01369000'], ['110675.50000000', '0.00005000']], 
                        'asks': [['110675.59000000', '6.58899000'], ['110675.60000000', '1.0000000'], ['110675.62000000', '0.00010000']]
                    }
        order_book_asks = extract_asks(order_book)
        assert calculate_price(order_book_asks, purchase_qty) == 830066.9341101
    

    



