
from pymongo import MongoClient
from datetime import datetime, timedelta
import argparse


client = MongoClient('mongodb://root:root@localhost:27017')
db = client['seguridad-monitoreo']
collection = db['logs']


def get_logs(module, start_date, end_date):
    query = {
        "module": module,
        "timestamp": {
            "$gte": start_date,
            "$lte": end_date,
        }
    }
    return list(collection.find(query)) 


def calculate_availability(logs):
    # Calcula la tasa de éxito y la tasa de fallo
    success_count = 0
    error_count = 0
    for log in logs:
        if log["status_code"] == 200:
            success_count += 1
        else:
            error_count += 1

    total_requests = success_count + error_count
    if total_requests == 0:
        return 0.0  # Evita la división por cero
    availability = float(error_count) / total_requests
    return 1 - availability  # Tasa de éxito = 1 - Tasa de fallo


def calculate_latency(module, start_date, end_date):
    # print(f'start_date: {start_date}')
    # print(f'end_date: {end_date}')
    days_difference = (end_date - start_date).days + 1  # Suma 1 para incluir ambos extremos
# Crea una lista de días entre start_date y end_date
    date_list = [start_date + timedelta(days=day) for day in range(days_difference)]
    # print(date_list)
    latencies = []  # Lista para almacenar las disponibilidades de cada día
    for date in date_list:
        # print('paso')
        current_date = date.strftime('%d/%m/%Y')
        day_start = datetime.strptime(current_date + ' 00:00:00', '%d/%m/%Y %H:%M:%S')
        day_end = datetime.strptime(current_date + ' 23:59:59', '%d/%m/%Y %H:%M:%S') 

        logs = get_logs(module, day_start, day_end)
        # print(logs)
        total_latency = sum(log["execution_time"] for log in logs)
        # print(f'total_latency: {total_latency}')
        if len(logs) == 0:
            latencies.append((day_start, total_latency))
        else:
            # print(f'total_latency: {total_latency}')
            # print(f'len(logs): {len(logs)}')
            value_latency_ms = float(total_latency)/len(logs)
            # print(f'value_latency_ms: {value_latency_ms}')
            latencies.append((day_start,float(value_latency_ms)))
    return latencies

def check_availability(module, days):
    # Calcula la disponibilidad para los últimos 'days' días
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    availabilities = []  # Lista para almacenar las disponibilidades de cada día

    for day in range(days):
        # Calcula la fecha de inicio y fin para el día actual
        day_start = start_date + timedelta(days=day)
        day_end = start_date + timedelta(days=day + 1)

        logs = get_logs(module, day_start, day_end)
        availability = calculate_availability(logs)
        availabilities.append((day_start, availability))

    return availabilities


# def check_latency(module, start_date, end_date):
#     # Calcula la latencia promedio para un período específico
#     latency = calculate_latency(module,start_date, end_date)
#     return latency


def render_graph(data, dates):
    max_data = max(data)
    num_rows = 11
    graph = []

    # Create the row with values at the top
    value_row = " " * 5  # Initial padding
    for value in data:
        if isinstance(value, int):
            value_str = f"{value:^8d}"
        else:
            value_str = f"{value:^8.2f}"  # Format as a float with 2 decimal places
        value_row += value_str.center(10) + " " * 2
    graph.append(value_row)

    # Vertical bar graph (from bottom up)
    for row in range(num_rows - 1, -1, -1):
        graph_row = " " * 5  # Initial padding
        for value in data:
            bar = " " * 2
            if max_data != 0:
                bar = "*" * int(value / max_data * 20)
            graph_row += bar[row * 2:row * 2 + 2].center(10) + " " * 2
        graph.append(graph_row)

    date_row = " " * 5  # Initial padding
    for date in dates:
        date_str = f"{date:^8s}"
        date_row += date_str.center(10) + " " * 2
    graph.append(date_row)

    return "\n".join(graph)

# CLI functions
def check_availability_cli(module, days):
    availabilities = check_availability(module, days)
    for date, availability in availabilities:
        print(f"{date.strftime('%d/%m/%Y')} {availability * 100:.1f}%")

def check_latency_cli(module, start_date, end_date):
    # start_date = datetime.strptime(start_date, '%d/%m/%Y')
    # end_date = datetime.strptime(end_date, '%d/%m/%Y')
    latencies = calculate_latency(module, start_date, end_date)
    for date, latency in latencies:
          print(f"{(date).strftime('%d/%m/%Y')}: {round(latency*1000,3)} ms")

def render_graph_cli(graph_type, days, module):
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    if graph_type == "Latency":
        latencies = calculate_latency(module, start_date, end_date)
        latency_values = [latency for _, latency in latencies]
        dates = [date.strftime('%d/%m/%Y') for date, _ in latencies]
        print(render_graph(latency_values, dates))
    elif graph_type == "Availability":
        availabilities = check_availability(module, days)
        availability_values = [availability * 100 for _, availability in availabilities]
        dates = [date.strftime('%d/%m/%Y') for date, _ in availabilities]
        print(render_graph(availability_values, dates))

def main():
    parser = argparse.ArgumentParser(description="Log Analysis CLI")
    subparsers = parser.add_subparsers(dest="action")

    # Subparser for the "CheckAvailability" command
    check_availability_parser = subparsers.add_parser("CheckAvailability")
    check_availability_parser.add_argument("module", choices=["PokeImages", "PokeApi", "PokeSearch", "PokeStats"])
    check_availability_parser.add_argument("-d", "--days", type=int, help="Number of days")

    # Subparser for the "CheckLatency" command
    check_latency_parser = subparsers.add_parser("CheckLatency")
    check_latency_parser.add_argument("module", choices=["PokeImages", "PokeApi", "PokeSearch", "PokeStats"])
    check_latency_parser.add_argument("--start-date", type=lambda d: datetime.strptime(d, '%d/%m/%Y'), help="Start date (dd/mm/yyyy)")
    check_latency_parser.add_argument("--end-date", type=lambda d: datetime.strptime(d, '%d/%m/%Y'), help="End date (dd/mm/yyyy)")

    # Subparser for the "RenderGraph" command
    render_graph_parser = subparsers.add_parser("RenderGraph")
    render_graph_parser.add_argument("module", choices=["PokeImages", "PokeApi", "PokeSearch", "PokeStats"])
    render_graph_parser.add_argument("--graph-type", choices=["Latency", "Availability"], help="Graph type")
    render_graph_parser.add_argument("-d", "--days", type=int, help="Number of days")

    args = parser.parse_args()

    if args.action == "CheckAvailability":
        check_availability_cli(args.module, args.days)
    elif args.action == "CheckLatency":
        check_latency_cli(args.module, args.start_date, args.end_date)
    elif args.action == "RenderGraph":
        render_graph_cli(args.graph_type, args.days, args.module)

if __name__ == "__main__":
    main()