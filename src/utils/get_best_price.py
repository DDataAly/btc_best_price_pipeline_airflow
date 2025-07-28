from src.utils.helpers import get_request_time


def find_best_price(exchanges: list, path: str, vol_per_order: float) -> list:
    prices = []
    request_time = get_request_time()
    for exchange in exchanges:
        snapshot = exchange.request_order_book_snapshot()
        snapshot = exchange.trim_snapshot(snapshot)
        exchange.save_order_book_snapshot(snapshot, path, request_time)

        price_volume_df = exchange.parse_snapshot_to_df(snapshot)
        try:
            exchange.order_cost_total = exchange.calculate_order_price(
                price_volume_df, vol_per_order
            )
            prices.append((float(exchange.order_cost_total), exchange.name))
        except TypeError:
            continue

    if prices:
        prices.sort()
        best_price = list(prices[0])
        best_price.append(request_time)
        return best_price
    else:
        return ["Not available", "Checked all exchanges", request_time]
