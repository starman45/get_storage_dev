import json
import requests
import subprocess


def get_list_db(url):
    action_url = "http://{}/web/database/list".format(url)
    data = {"params": {}}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(action_url, json=data, headers=headers)
        db = response.json()
    except Exception as e:
        print("URL:", url)
        print("Connection establishment failed!")
        print(e)
        print("------------------------------")
        db = {"error": e}

    return db


def transform_to_GB(size):
    size = size.replace(",", ".")
    if "K" in size:
        size = float(size[:size.index("K")]) / 1000000
    elif "M" in size:
        size = float(size[:size.index("M")]) / 1000
    elif "G" in size:
        size = float(size[:size.index("G")])
    return size


def sum_items(all_items):
    return sum(map(float, all_items))


def execute_bash_script(db_name):
    try:
        operation = subprocess.check_output('sh get_storage.sh {}'.format(db_name), shell=True).decode('utf-8')
        output_from_script = operation.splitlines()
        filestore_size = output_from_script[-2]
        db_size = output_from_script[-1]
    except Exception as e:
        dump_name = False
        print("Error:")
        print(e)
        return None, None
    return filestore_size, db_size


def get_info(list_db):
    rds_factor = 0.115
    ec2_factor = 0.1
    all_sizes = []
    all_prices = []

    for db in list_db:
        print('DATABASE:', db)
        sizes = execute_bash_script(db)
        if sizes is None:
            continue
        db_size = transform_to_GB(sizes[-1][9:-1])
        filestore_size = transform_to_GB(sizes[-2][16:20])

        db_size_price = '%.3f' % (rds_factor * db_size)

        print("db_size:", db_size, "GB", f" --> {db_size_price} $", "\n")

        all_sizes.append(db_size)
        all_prices.append(db_size_price)

    if len(list_db) == 0:
        print("No databases found")
        return

    filestore_size_price = '%.3f' % (ec2_factor * filestore_size)
    print("filestore_size:", filestore_size, "GB", f" --> {filestore_size_price} $", "\n")

    all_sizes.append(filestore_size)
    all_prices.append(filestore_size_price)

    sum_all_sizes = '%.3f' % sum_items(all_sizes)
    summ_all_prices = '%.3f' % sum_items(all_prices)

    print("TOTAL ----->", sum_all_sizes, "GB", f" Costo ---> {summ_all_prices} $")


def generate_report(url):
    db = get_list_db(url)
    if db.get('error'):
        print('¡CONNECTION PROBLEM!\nReview data and try again.')
    else:
        list_db = db['result']
        get_info(list_db)


def main():
    generate_report('0.0.0.0:8069')


if __name__ == '__main__':
    main()

