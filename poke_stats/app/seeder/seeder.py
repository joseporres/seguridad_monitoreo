

from app.config.mongo import pokemons 
import csv


def run():
    print("Seeding pokemons")
    csvfile = open('Pokemon.csv', 'r')
    reader = csv.DictReader(csvfile)
    for each in reader:
        row = {}
        for field in reader.fieldnames:
            row[field] = each[field]
        pokemons.insert_one(row)
    
  
if __name__ == "__main__":
    run()
