import pytest
from sandbox.binance_prep_4 import (
    fetch_snapshot, 
    extract_asks,
    sufficient_depth,
    match_order_to_order_book_asks,
    calculate_purchase_price,
    convert_output_to_strings,
    InvalidOrderBook, 
    InsufficientOrderBookDepth
)

url = 'https://api.binance.com/api/v3/depth'
params = 'symbol=BTCUSDT&limit=3'

class TestFetchSnapshot:
    @pytest.mark.it('Returns valid snapshot')
    def test_valid_snapshot(self):
        snapshot = fetch_snapshot(url, params)
        assert isinstance(snapshot, dict)
        assert 'asks' in snapshot.keys()
        assert 'bids' in snapshot.keys()


class TestExtractAsks:
    @pytest.mark.it('Returns asks if present')
    def test_returns_asks(self):
        snapshot = {'lastUpdateId': 75955349533, 
            'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
            'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '0.00010000'], ['111443.36000000', '0.00015000']]
            }
        order_book_asks = extract_asks(snapshot)
        assert order_book_asks == [['111443.28000000', '4.82829000'], ['111443.29000000', '0.00010000'], ['111443.36000000', '0.00015000']]

    @pytest.mark.it('Raises error if asks value is missing')
    def test_raises_error_missing_asks_value(self):
        snapshot = {'lastUpdateId': 75955349533, 
            'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
            'asks': []
            }
        with pytest.raises(InvalidOrderBook):
            order_book_asks = extract_asks(snapshot)

    @pytest.mark.it('Raises error if asks key is missing')
    def test_raises_error_missing_asks_key(self):
        snapshot = {'lastUpdateId': 75955349533, 
            'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
            }
        with pytest.raises(InvalidOrderBook):
            order_book_asks = extract_asks(snapshot)

class TestSufficientDepth:
    @pytest.mark.it('Returns True if order book depth is sufficient')
    def test_returns_true(self):
        snapshot = {'lastUpdateId': 75955349533, 
            'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
            'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '0.00010000'], ['111443.36000000', '0.00015000']]
            }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 0.5
        assert sufficient_depth(order_book_asks, purchase_qty)

    @pytest.mark.it('Raises error if order book depth is not sufficient')
    def test_raises_error(self):
        snapshot = {'lastUpdateId': 75955349533, 
            'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
            'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '0.00010000'], ['111443.36000000', '0.00015000']]
            }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 20
        with pytest.raises(InsufficientOrderBookDepth):
            sufficient_depth(order_book_asks, purchase_qty)

class TestMatchOrderToOrderBookAsks:
    def test_returns_correct_match_one_ask_sufficient(self):
        snapshot = {'lastUpdateId': 75955349533, 
        'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
        'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '0.00010000'], ['111443.36000000', '0.00015000']]
        }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 2
        assert(match_order_to_order_book_asks(order_book_asks, purchase_qty)) == [[111443.28000000, 2.0]]

    def test_handles_fractured_match(self):
        snapshot = {'lastUpdateId': 75955349533, 
        'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
        'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '1.00010000'], ['111443.36000000', '0.00015000']]
        }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 5
        assert(match_order_to_order_book_asks(order_book_asks, purchase_qty)) == [[111443.28000000, 4.82829000], [111443.29000000, (5-4.82829000)]]
        
    def test_raises_error_insufficient_depth(self):
        snapshot = {'lastUpdateId': 75955349533, 
        'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
        'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '1.00010000'], ['111443.36000000', '0.00015000']]
        }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 50
        with pytest.raises(InsufficientOrderBookDepth):
            match_order_to_order_book_asks(order_book_asks, purchase_qty)
        
        
class TestCalculatePurchasePrice:
    def test_calculates_price_correctly(self):
        snapshot = {'lastUpdateId': 75955349533, 
        'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
        'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '1.00010000'], ['111443.36000000', '0.00015000']]
        }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 5   
        matched_asks = match_order_to_order_book_asks(order_book_asks, purchase_qty)
        assert calculate_purchase_price(matched_asks) == pytest.approx((4.82829000*111443.28000000 + (-4.82829000+5)*111443.29000000), rel=1e-9)

class TestConvertOutputToString:
    @pytest.mark.it ('converts floats to strings to match Binance API output format')
    def test_outputs_lists_of_strings(self):
        snapshot = {'lastUpdateId': 75955349533, 
        'bids': [['111443.27000000', '6.64726000'], ['111443.26000000', '0.00214000'], ['111443.24000000', '0.00525000']],
        'asks': [['111443.28000000', '4.82829000'], ['111443.29000000', '1.00010000'], ['111443.36000000', '0.00015000']]
        }
        order_book_asks = extract_asks(snapshot)
        purchase_qty = 5   
        matched_asks = match_order_to_order_book_asks(order_book_asks, purchase_qty)
        output = convert_output_to_strings(matched_asks)
        format_checker = True
        for [price, qty] in output:
            if not isinstance(price, str) or not isinstance(qty, str):
                format_checker = False
                break
            if len(price[(price.find('.'))+1:])!=8 or len(qty[(qty.find('.'))+1:])!=8:
                format_checker = False
                break
        assert format_checker == True





