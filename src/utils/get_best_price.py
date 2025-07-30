import logging
from src.utils.helpers import get_request_time


def find_best_price(exchanges: list, path: str, vol_per_order: float) -> list:
    prices = []
    request_time = get_request_time()
    for exchange in exchanges:
        try:
            snapshot = exchange.request_order_book_snapshot()
            # if snapshot is None or exchange.validate_snapshot(snapshot) is False:
            if exchange.validate_snapshot(snapshot) is False:
                logging.warning(
                    f"{exchange.name}: invalid or missing snapshot at {request_time}"
                )
                continue

            snapshot = exchange.trim_snapshot(snapshot)
            exchange.save_order_book_snapshot(snapshot, path, request_time)

            price_volume_df = exchange.parse_snapshot_to_df(snapshot)
            exchange.order_cost_total = exchange.calculate_order_price(
                price_volume_df, vol_per_order
            )
            prices.append((float(exchange.order_cost_total), exchange.name))

        except TypeError:
            logging.error(f"Type error when parsing {exchange.name} snapshot.")
        except Exception as e:
            logging.error(f"{exchange.name} An error has occurred: {e}")

    if prices:
        prices.sort()
        best_price = list(prices[0])
        best_price.append(request_time)
        return best_price
    else:
        logging.warning(
            f"No exchanges could provide a valid price at {request_time}."
            " Increase the order book depth or split order on more transactions"
        )
        return ["Not available", "Checked all exchanges", request_time]
