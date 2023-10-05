# app.py
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/get_pokemon/<string:id_or_name>', methods=['GET'])
def get_pokemon(id_or_name):
    try:
        # Construct the URL for the PokeAPI using the id_or_name parameter
        pokeapi_url = f'https://pokeapi.co/api/v2/pokemon/{id_or_name}/'

        # Send a GET request to the PokeAPI
        response = requests.get(pokeapi_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract the desired information (e.g., name, abilities, types, etc.)
            pokemon_info = {
                'Name': data['name'],
                'Abilities': [ability['ability']['name'] for ability in data['abilities']],
                'Types': [type['type']['name'] for type in data['types']],
                # Add more attributes as needed
            }

            return jsonify(pokemon_info), 200
        else:
            # Return an error message if the request was not successful
            return jsonify({'error': 'Pokemon not found'}), 404

    except Exception as e:
        # Handle exceptions (e.g., network errors)
        return jsonify({'error': 'An error occurred'}), 500
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')