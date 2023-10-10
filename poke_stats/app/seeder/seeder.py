

from app.config.mongo import pokemons 
import csv



def is_pokemons_empty():
    return pokemons.count_documents({}) == 0


def run():
    if is_pokemons_empty():
        print("Seeding pokemons")
        csvfile = open('Pokemon.csv', 'r')
        reader = csv.DictReader(csvfile)
        for each in reader:
            row = {}
            for field in reader.fieldnames:
                row[field] = each[field].lower()
            pokemons.insert_one(row)
    else:
        print("Pokemons collection already contains data. Skipping seeding.")
    
  
if __name__ == "__main__":
    run()
