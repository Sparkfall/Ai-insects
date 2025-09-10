from flask import Flask, request, jsonify, make_response
import psycopg2
from psycopg2.extras import RealDictCursor
import jwt
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = '3b6dc7732e7647d85f0dcbb44b337b504d1cc03870a358d290f14409bb912217'  

def get_db_connection():
    conn = psycopg2.connect(
        dbname='insect',
        user='postgres',
        password="admin",
        host='localhost',
        port='7890'
    )
    return conn

def execute_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params)
    conn.commit()
    result = cursor.fetchall() if cursor.rowcount > 1 else cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def token_required(f):
    def wrapper(*args, **kwargs):
        #token = request.headers.get('Authorization')
        #if not token:
        #    return jsonify({'status': 'error', 'message': 'Token is missing!'}), 403
        #try:
        #    token = token.split(" ")[1]
        #    jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        #except Exception as e:
        #    return jsonify({'status': 'error', 'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.json
    phone = data.get('phone')
    # Update the query to use phone
    user = execute_query('SELECT * FROM users WHERE phone = %s', (phone,))
    if not user:
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    token = jwt.encode({
        'user': user['phone'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'status': 'success', 'message': 'Login successful', 'data': {'token': token}})

@app.route('/api/v1/auth/logout', methods=['POST'])
@token_required
def logout():
    return jsonify({'status': 'success', 'message': 'Logout successful'})

@app.route('/api/v1/users', methods=['GET'])
@token_required
def get_users():
    users = execute_query('SELECT * FROM users')
    return jsonify({'status': 'success', 'data': users})

@app.route('/api/v1/users', methods=['POST'])
@token_required
def create_user():
    data = request.json
    query = """
    INSERT INTO users (name, phone, privilege, date)
    VALUES (%s, %s, %s, %s) RETURNING id, name, phone, privilege, date
    """
    params = (data['name'], data['phone'], data['privilege'], datetime.datetime.utcnow())
    user = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'User created successfully', 'data': user})

@app.route('/api/v1/users/<int:id>', methods=['PUT'])
@token_required
def update_user(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE users SET {fields} WHERE id = %s RETURNING id, name, phone, privilege, date"
    params = (*data.values(), id)
    user = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'User updated successfully', 'data': user})

@app.route('/api/v1/users/<int:id>', methods=['DELETE'])
@token_required
def delete_user(id):
    execute_query('DELETE FROM users WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'User deleted successfully'})

@app.route('/api/v1/vibrio_sp', methods=['GET'])
@token_required
def get_vibrio_sp():
    vibrio_sp = execute_query('SELECT * FROM vibrio_sp')
    return jsonify({'status': 'success', 'data': vibrio_sp})

@app.route('/api/v1/ponds', methods=['GET'])
@token_required
def get_ponds():
    ponds = execute_query('SELECT * FROM ponds')
    return jsonify({'status': 'success', 'data': ponds})

@app.route('/api/v1/ponds', methods=['POST'])
@token_required
def create_pond():
    data = request.json
    query = """
    INSERT INTO ponds (name, mark, room_no, height, width, volume, status, user_id, date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, name, mark, room_no, height, width, volume, status, user_id, date
    """
    params = (data['name'], data['mark'], data['room_no'], data['height'], data['width'], data['volume'], data['status'], data['user_id'], data['date'])
    pond = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Pond created successfully', 'data': pond})

@app.route('/api/v1/ponds/<int:id>', methods=['PUT'])
@token_required
def update_pond(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE ponds SET {fields} WHERE id = %s RETURNING id, name, mark, room_no, height, width, volume, status, user_id, date"
    params = (*data.values(), id)
    pond = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Pond updated successfully', 'data': pond})

@app.route('/api/v1/ponds/<int:id>', methods=['DELETE'])
@token_required
def delete_pond(id):
    execute_query('DELETE FROM ponds WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Pond deleted successfully'})

@app.route('/api/v1/indicator-types', methods=['GET'])
@token_required
def get_indicator_types():
    indicator_types = execute_query('SELECT * FROM indicator_types')
    return jsonify({'status': 'success', 'data': indicator_types})

@app.route('/api/v1/indicator-types', methods=['POST'])
@token_required
def create_indicator_type():
    data = request.json
    query = "INSERT INTO indicator_types (name) VALUES (%s) RETURNING id, name"
    indicator_type = execute_query(query, (data['name'],))
    return jsonify({'status': 'success', 'message': 'Indicator type created successfully', 'data': indicator_type})

@app.route('/api/v1/indicator-types/<int:id>', methods=['PUT'])
@token_required
def update_indicator_type(id):
    data = request.json
    query = "UPDATE indicator_types SET name = %s WHERE id = %s RETURNING id, name"
    indicator_type = execute_query(query, (data['name'], id))
    return jsonify({'status': 'success', 'message': 'Indicator type updated successfully', 'data': indicator_type})

@app.route('/api/v1/indicator-types/<int:id>', methods=['DELETE'])
@token_required
def delete_indicator_type(id):
    execute_query('DELETE FROM indicator_types WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Indicator type deleted successfully'})

@app.route('/api/v1/indicator-items', methods=['GET'])
@token_required
def get_indicator_items():
    indicator_items = execute_query('SELECT * FROM indicator_items')
    return jsonify({'status': 'success', 'data': indicator_items})

@app.route('/api/v1/indicator-items', methods=['POST'])
@token_required
def create_indicator_item():
    data = request.json
    query = """
    INSERT INTO indicator_items (ind_type_id, name, spec)
    VALUES (%s, %s, %s) RETURNING id, ind_type_id, name, spec
    """
    params = (data['ind_type_id'], data['name'], data['spec'])
    indicator_item = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Indicator item created successfully', 'data': indicator_item})

@app.route('/api/v1/indicator-items/<int:id>', methods=['PUT'])
@token_required
def update_indicator_item(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE indicator_items SET {fields} WHERE id = %s RETURNING id, ind_type_id, name, spec"
    params = (*data.values(), id)
    indicator_item = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Indicator item updated successfully', 'data': indicator_item})

@app.route('/api/v1/indicator-items/<int:id>', methods=['DELETE'])
@token_required
def delete_indicator_item(id):
    execute_query('DELETE FROM indicator_items WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Indicator item deleted successfully'})


@app.route('/api/v1/shrimp_growth', methods=['GET'])
@token_required
def get_shrimp_growth():
    shrimp_growth = execute_query('SELECT * FROM shrimp_growth')
    return jsonify({'status': 'success', 'data': shrimp_growth})

@app.route('/api/v1/shrimp_growth', methods=['POST'])
@token_required
def create_shrimp_growth():
    data = request.json
    query = """
    INSERT INTO shrimp_growth (shrimp_count, weight_per_shrimp, daily_growth_rate, survival_rate, uniformity, date, repetition, cultivation_time, body_length, total_weight, stage_name, measurer, pond_name, mark, spec)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, shrimp_count, weight_per_shrimp, daily_growth_rate, survival_rate, uniformity, date, repetition, cultivation_time, body_length, total_weight, stage_name, measurer, pond_name, mark, spec
    """
    params = (data['shrimp_count'], data['weight_per_shrimp'], data['daily_growth_rate'], data['survival_rate'], data['uniformity'], data['date'], data['repetition'], data['cultivation_time'], data['body_length'], data['total_weight'], data['stage_name'], data['measurer'], data['pond_name'], data['mark'], data['spec'])
    shrimp_growth_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Shrimp growth record created successfully', 'data': shrimp_growth_record})

@app.route('/api/v1/shrimp_growth/<int:id>', methods=['PUT'])
@token_required
def update_shrimp_growth(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE shrimp_growth SET {fields} WHERE id = %s RETURNING id, shrimp_count, weight_per_shrimp, daily_growth_rate, survival_rate, uniformity, date, repetition, cultivation_time, body_length, total_weight, stage_name, measurer, pond_name, mark, spec"
    params = (*data.values(), id)
    shrimp_growth_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Shrimp growth record updated successfully', 'data': shrimp_growth_record})

@app.route('/api/v1/shrimp_growth/<int:id>', methods=['DELETE'])
@token_required
def delete_shrimp_growth(id):
    execute_query('DELETE FROM shrimp_growth WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Shrimp growth record deleted successfully'})


@app.route('/api/v1/feeding', methods=['GET'])
@token_required
def get_feeding():
    feeding = execute_query('SELECT * FROM feeding')
    return jsonify({'status': 'success', 'data': feeding})

@app.route('/api/v1/feeding', methods=['POST'])
@token_required
def create_feeding():
    data = request.json
    query = """
    INSERT INTO feeding (cumulative_feed, feed_growth_rate, water_added, cumulative_water_added, water_discharged, cumulative_water_discharged, carbon_source_added, daily_carbon_source_added, date, feed_6am, feed_10am, feed_2pm, feed_6pm, feed_10pm, daily_feed, stage_name, water_treatment_method, pond_name, mark, feed_stage, feed_mixture, shrimp_status, pathogen)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, cumulative_feed, feed_growth_rate, water_added, cumulative_water_added, water_discharged, cumulative_water_discharged, carbon_source_added, daily_carbon_source_added, date, feed_6am, feed_10am, feed_2pm, feed_6pm, feed_10pm, daily_feed, stage_name, water_treatment_method, pond_name, mark, feed_stage, feed_mixture, shrimp_status, pathogen
    """
    params = (
        data['cumulative_feed'], data['feed_growth_rate'], data['water_added'], data['cumulative_water_added'], data['water_discharged'], data['cumulative_water_discharged'], data['carbon_source_added'], data['daily_carbon_source_added'], data['date'], data['feed_6am'], data['feed_10am'], data['feed_2pm'], data['feed_6pm'], data['feed_10pm'], data['daily_feed'], data['stage_name'], data['water_treatment_method'], data['pond_name'], data['mark'], data['feed_stage'], data['feed_mixture'], data['shrimp_status'], data['pathogen']
    )
    feeding_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Feeding record created successfully', 'data': feeding_record})

@app.route('/api/v1/feeding/<int:id>', methods=['PUT'])
@token_required
def update_feeding(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE feeding SET {fields} WHERE id = %s RETURNING id, cumulative_feed, feed_growth_rate, water_added, cumulative_water_added, water_discharged, cumulative_water_discharged, carbon_source_added, daily_carbon_source_added, date, feed_6am, feed_10am, feed_2pm, feed_6pm, feed_10pm, daily_feed, stage_name, water_treatment_method, pond_name, mark, feed_stage, feed_mixture, shrimp_status, pathogen"
    params = (*data.values(), id)
    feeding_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Feeding record updated successfully', 'data': feeding_record})

@app.route('/api/v1/feeding/<int:id>', methods=['DELETE'])
@token_required
def delete_feeding(id):
    execute_query('DELETE FROM feeding WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Feeding record deleted successfully'})


@app.route('/api/v1/water_body_measurement', methods=['GET'])
@token_required
def get_water_body_measurement():
    water_body_measurement = execute_query('SELECT * FROM water_body_measurement')
    return jsonify({'status': 'success', 'data': water_body_measurement})

@app.route('/api/v1/water_body_measurement', methods=['POST'])
@token_required
def create_water_body_measurement():
    data = request.json
    query = """
    INSERT INTO water_body_measurement (ph, dissolved_oxygen, temperature, salinity, date, pond_id, repetition, time, temp_min, temp_max, stage_id, weather, measurer, mark)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, ph, dissolved_oxygen, temperature, salinity, date, pond_id, repetition, time, temp_min, temp_max, stage_id, weather, measurer, mark
    """
    params = (
        data['ph'], data['dissolved_oxygen'], data['temperature'], data['salinity'], data['date'], data['pond_id'], data['repetition'], data['time'], data['temp_min'], data['temp_max'], data['stage_id'], data['weather'], data['measurer'], data['mark']
    )
    water_body_measurement_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Water body measurement record created successfully', 'data': water_body_measurement_record})

@app.route('/api/v1/water_body_measurement/<int:id>', methods=['PUT'])
@token_required
def update_water_body_measurement(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE water_body_measurement SET {fields} WHERE id = %s RETURNING id, ph, dissolved_oxygen, temperature, salinity, date, pond_id, repetition, time, temp_min, temp_max, stage_id, weather, measurer, mark"
    params = (*data.values(), id)
    water_body_measurement_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Water body measurement record updated successfully', 'data': water_body_measurement_record})

@app.route('/api/v1/water_body_measurement/<int:id>', methods=['DELETE'])
@token_required
def delete_water_body_measurement(id):
    execute_query('DELETE FROM water_body_measurement WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Water body measurement record deleted successfully'})


@app.route('/api/v1/water_treatment', methods=['GET'])
@token_required
def get_water_treatment():
    water_treatment = execute_query('SELECT * FROM water_treatment')
    return jsonify({'status': 'success', 'data': water_treatment})

@app.route('/api/v1/water_treatment', methods=['POST'])
@token_required
def create_water_treatment():
    data = request.json
    query = """
    INSERT INTO water_treatment (potassium_chloride, magnesium_sulfate, baking_soda, date, fermented_feed, molasses, bacillus_em, general_em_bacteria, photosynthetic_bacteria, taurine, calcium_supplement, trace_elements, multivitamins, vitamin_c, protein_calcium, dolomite_powder, potassium_carbonate, amino_acids, stress_high_calcium, magnesium_chloride, lactic_acid_bacteria, stage_name, mark, pond_name)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, potassium_chloride, magnesium_sulfate, baking_soda, date, fermented_feed, molasses, bacillus_em, general_em_bacteria, photosynthetic_bacteria, taurine, calcium_supplement, trace_elements, multivitamins, vitamin_c, protein_calcium, dolomite_powder, potassium_carbonate, amino_acids, stress_high_calcium, magnesium_chloride, lactic_acid_bacteria, stage_name, mark, pond_name
    """
    params = (
        data['potassium_chloride'], data['magnesium_sulfate'], data['baking_soda'], data['date'], data['fermented_feed'], data['molasses'], data['bacillus_em'], data['general_em_bacteria'], data['photosynthetic_bacteria'], data['taurine'], data['calcium_supplement'], data['trace_elements'], data['multivitamins'], data['vitamin_c'], data['protein_calcium'], data['dolomite_powder'], data['potassium_carbonate'], data['amino_acids'], data['stress_high_calcium'], data['magnesium_chloride'], data['lactic_acid_bacteria'], data['stage_name'], data['mark'], data['pond_name']
    )
    water_treatment_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Water treatment record created successfully', 'data': water_treatment_record})

@app.route('/api/v1/water_treatment/<int:id>', methods=['PUT'])
@token_required
def update_water_treatment(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE water_treatment SET {fields} WHERE id = %s RETURNING id, potassium_chloride, magnesium_sulfate, baking_soda, date, fermented_feed, molasses, bacillus_em, general_em_bacteria, photosynthetic_bacteria, taurine, calcium_supplement, trace_elements, multivitamins, vitamin_c, protein_calcium, dolomite_powder, potassium_carbonate, amino_acids, stress_high_calcium, magnesium_chloride, lactic_acid_bacteria, stage_name, mark, pond_name"
    params = (*data.values(), id)
    water_treatment_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Water treatment record updated successfully', 'data': water_treatment_record})

@app.route('/api/v1/water_treatment/<int:id>', methods=['DELETE'])
@token_required
def delete_water_treatment(id):
    execute_query('DELETE FROM water_treatment WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Water treatment record deleted successfully'})

@app.route('/api/v1/water_quality_measurement', methods=['GET'])
@token_required
def get_water_quality_measurement():
    water_quality_measurement = execute_query('SELECT * FROM water_quality_measurement')
    return jsonify({'status': 'success', 'data': water_quality_measurement})

@app.route('/api/v1/water_quality_measurement', methods=['POST'])
@token_required
def create_water_quality_measurement():
    data = request.json
    query = """
    INSERT INTO water_quality_measurement (nitrite, turbidity, total_alkalinity, date, pond_id, repetition, time, ammonia_nitrogen, stage_id, mark, measurer)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, nitrite, turbidity, total_alkalinity, date, pond_id, repetition, time, ammonia_nitrogen, stage_id, mark, measurer
    """
    params = (
        data['nitrite'], data['turbidity'], data['total_alkalinity'], data['date'], data['pond_id'], data['repetition'], data['time'], data['ammonia_nitrogen'], data['stage_id'], data['mark'], data['measurer']
    )
    water_quality_measurement_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Water quality measurement record created successfully', 'data': water_quality_measurement_record})

@app.route('/api/v1/water_quality_measurement/<int:id>', methods=['PUT'])
@token_required
def update_water_quality_measurement(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE water_quality_measurement SET {fields} WHERE id = %s RETURNING id, nitrite, turbidity, total_alkalinity, date, pond_id, repetition, time, ammonia_nitrogen, stage_id, mark, measurer"
    params = (*data.values(), id)
    water_quality_measurement_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Water quality measurement record updated successfully', 'data': water_quality_measurement_record})

@app.route('/api/v1/water_quality_measurement/<int:id>', methods=['DELETE'])
@token_required
def delete_water_quality_measurement(id):
    execute_query('DELETE FROM water_quality_measurement WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Water quality measurement record deleted successfully'})

@app.route('/api/v1/bacteria_measurement', methods=['GET'])
@token_required
def get_bacteria_measurement():
    bacteria_measurement = execute_query('SELECT * FROM bacteria_measurement')
    return jsonify({'status': 'success', 'data': bacteria_measurement})

@app.route('/api/v1/bacteria_measurement', methods=['POST'])
@token_required
def create_bacteria_measurement():
    data = request.json
    query = """
    INSERT INTO bacteria_measurement (total_bacteria_104, total_bacteria, vibrio_to_total_bacteria_percentage, date, pond_id, repetition, time, vibrio_yellow, vibrio_green, total_vibrio, stage_id, mark, measurer)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, total_bacteria_104, total_bacteria, vibrio_to_total_bacteria_percentage, date, pond_id, repetition, time, vibrio_yellow, vibrio_green, total_vibrio, stage_id, mark, measurer
    """
    params = (
        data['total_bacteria_104'], data['total_bacteria'], data['vibrio_to_total_bacteria_percentage'], data['date'], data['pond_id'], data['repetition'], data['time'], data['vibrio_yellow'], data['vibrio_green'], data['total_vibrio'], data['stage_id'], data['mark'], data['measurer']
    )
    bacteria_measurement_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Bacteria measurement record created successfully', 'data': bacteria_measurement_record})

@app.route('/api/v1/bacteria_measurement/<int:id>', methods=['PUT'])
@token_required
def update_bacteria_measurement(id):
    data = request.json
    fields = ', '.join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE bacteria_measurement SET {fields} WHERE id = %s RETURNING id, total_bacteria_104, total_bacteria, vibrio_to_total_bacteria_percentage, date, pond_id, repetition, time, vibrio_yellow, vibrio_green, total_vibrio, stage_id, mark, measurer"
    params = (*data.values(), id)
    bacteria_measurement_record = execute_query(query, params)
    return jsonify({'status': 'success', 'message': 'Bacteria measurement record updated successfully', 'data': bacteria_measurement_record})

@app.route('/api/v1/bacteria_measurement/<int:id>', methods=['DELETE'])
@token_required
def delete_bacteria_measurement(id):
    execute_query('DELETE FROM bacteria_measurement WHERE id = %s', (id,))
    return jsonify({'status': 'success', 'message': 'Bacteria measurement record deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
