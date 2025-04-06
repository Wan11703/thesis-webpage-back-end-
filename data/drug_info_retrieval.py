from flask import Flask, request, jsonify
from flask_cors import CORS  # Import Flask-CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

# Define the path to the CSV files
df_path = r'C:\Users\Mark\OneDrive\Desktop\thesis-webpage\data\drugbank_clean.csv'
df_prepared_path = r'C:\Users\Mark\OneDrive\Desktop\thesis-webpage\data\drug_information.csv'

def get_drug_info(drug_name):
    try:
        # Load DataFrames
        df_prepared = pd.read_csv(df_prepared_path, index_col="name")
        df = pd.read_csv(df_path, low_memory=False)  # Suppress DtypeWarning
        drug_name_lower = drug_name.lower()

        # Check if the drug exists in the database
        try:
            drug_info = df_prepared.loc[df_prepared.index.str.lower() == drug_name_lower].iloc[0]
        except IndexError:
            print(f"Drug '{drug_name}' not found in the database.")
            return None

        # Process drug interactions
        if isinstance(drug_info['drug-interactions'], str):
            interactions = drug_info['drug-interactions'].split()
            mapped_interactions = []
            for interaction_id in interactions:
                try:
                    drug_name_for_id = df[df['drugbank-id'].str.lower() == interaction_id.lower()]['name'].iloc[0]
                    mapped_interactions.append(drug_name_for_id)
                except IndexError:
                    pass
            drug_info['drug-interactions'] = ', '.join(mapped_interactions)

        # Extract drug information
        drug_information = drug_info['description']
        indication = drug_info['indication']
        side_effects = drug_info['pharmacodynamics']
        interaction = f"Food Interactions: {drug_info['food-interactions']}\nDrug Interactions: {drug_info['drug-interactions']}"

        return drug_information, indication, side_effects, interaction

    except (KeyError, IndexError) as e:
        print(f"Error processing drug information: {e}")
        return None

@app.route('/get-drug-info', methods=['POST'])
def get_drug_info_endpoint():
    data = request.get_json()
    drug_name = data.get('drug_name')
    result = get_drug_info(drug_name)

    if result:
        drug_information, indication, side_effects, interaction = result
        return jsonify({
            "drug_information": drug_information,
            "indication": indication,
            "side_effects": side_effects,
            "interaction": interaction
        })
    else:
        return jsonify({"error": f"Drug '{drug_name}' not found in the database."}), 404

if __name__ == '__main__':
    app.run(debug=True)