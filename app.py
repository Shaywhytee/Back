from flask import Flask, current_app, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_marshmallow import Marshmallow
from marshmallow import fields, Schema, post_dump
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import os
import jwt

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SECRET_KEY'] = 'shaywhytee'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class AccountInfo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_name = db.Column(db.String(50), nullable=False, unique=True)
  user_email = db.Column(db.String(50), nullable=False, unique=True)
  user_password_hash = db.Column(db.String(128), nullable=False)
  user_auth = db.Column(db.Integer, nullable=False)

  def __init__(self, user_name, user_email, user_password, user_auth):
    self.user_name = user_name
    self.user_email = user_email
    self.user_password_hash = user_password
    self.user_auth = user_auth
    
  def set_password(self, password):
    self.user_password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.user_password_hash, password)
    
class RMA(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  odoo_id = db.Column(db.Integer, nullable=False, unique=True)
  fd_sn = db.Column(db.String, nullable=False)
  bay = db.Column(db.Integer, nullable=False)
  technician_id = db.Column(db.Integer, db.ForeignKey('account_info.id'), nullable=False)
  technician = db.relationship('AccountInfo', foreign_keys=[technician_id])
  repair_status = db.Column(db.String)
  repair_notes = db.Column(db.String)
  repair_parts = db.Column(db.String)
  repair_completion = db.Column(db.Boolean, nullable=False, default=False)
  vac_status = db.relationship('VacStatus', back_populates='rma', uselist=False)
  freeze_status = db.relationship('FreezeStatus', back_populates='rma', uselist=False)
  heat_status = db.relationship('HeatStatus', back_populates='rma', uselist=False)
  module_status = db.relationship('ModuleStatus', back_populates='rma', uselist=False)

  def __init__(self, odoo_id, fd_sn, bay, technician_id, repair_status, repair_notes, repair_parts, repair_completion):
    self.odoo_id = odoo_id
    self.fd_sn = fd_sn
    self.bay = bay
    self.technician_id = technician_id
    self.repair_status = repair_status
    self.repair_notes = repair_notes
    self.repair_parts = repair_parts
    self.repair_completion = repair_completion



rma_main_id = 'rma.id'    
class VacStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  pump_type = db.Column(db.String)
  pump_sn = db.Column(db.String)
  pump_mtorr_1000 = db.Column(db.Integer)
  pump_mtorr_500 = db.Column(db.Integer)
  pump_mtorr_300 = db.Column(db.Integer)
  pump_mtorr_200 = db.Column(db.Integer)
  pump_mtorr_bo = db.Column(db.Integer)
  mtorr_1000 = db.Column(db.Integer)
  mtorr_500 = db.Column(db.Integer)
  mtorr_300 = db.Column(db.Integer)
  mtorr_200 = db.Column(db.Integer)
  mtorr_bo = db.Column(db.Integer)
  rma_id = db.Column(db.Integer, db.ForeignKey(rma_main_id))
  rma = db.relationship('RMA', back_populates='vac_status')

  def __init__(self, pump_type, pump_sn, pump_mtorr_1000, pump_mtorr_500, pump_mtorr_300, pump_mtorr_200, pump_mtorr_bo, mtorr_1000, mtorr_500, mtorr_300, mtorr_200, mtorr_bo, rma):
    self.pump_type = pump_type
    self.pump_sn = pump_sn
    self.pump_mtorr_1000 = pump_mtorr_1000
    self.pump_mtorr_500 = pump_mtorr_500
    self.pump_mtorr_300 = pump_mtorr_300
    self.pump_mtorr_200 = pump_mtorr_200
    self.pump_mtorr_bo = pump_mtorr_bo
    self.mtorr_1000 = mtorr_1000
    self.mtorr_500 = mtorr_500
    self.mtorr_300 = mtorr_300
    self.mtorr_200 = mtorr_200
    self.mtorr_bo = mtorr_bo
    self.rma = rma

class FreezeStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  coil_count = db.Column(db.String)
  amp_reading = db.Column(db.Integer)
  temp_front = db.Column(db.Integer)
  temp_mid = db.Column(db.Integer)
  temp_back = db.Column(db.Integer)
  rma_id = db.Column(db.Integer, db.ForeignKey(rma_main_id), nullable=False)
  rma = db.relationship('RMA', back_populates='freeze_status')

  def __init__(self, coil_count, amp_reading, temp_front, temp_mid, temp_back, rma):
    self.coil_count = coil_count
    self.amp_reading = amp_reading
    self.temp_front = temp_front
    self.temp_mid = temp_mid
    self.temp_back = temp_back
    self.rma = rma

class HeatStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ambient = db.Column(db.Integer)
  heat_limit = db.Column(db.Integer)
  max_temp = db.Column(db.Integer)
  pad_one = db.Column(db.Integer)
  pad_two = db.Column(db.Integer)
  pad_three = db.Column(db.Integer)
  pad_four = db.Column(db.Integer)
  pad_five = db.Column(db.Integer)
  pad_six = db.Column(db.Integer)
  rma_id = db.Column(db.Integer, db.ForeignKey(rma_main_id), nullable=False)
  rma = db.relationship('RMA', back_populates='heat_status')

  def __init__(self, ambient, heat_limit, max_temp, pad_one, pad_two, pad_three, pad_four, pad_five, pad_six, rma):
    self.ambient = ambient
    self.heat_limit = heat_limit
    self.max_temp = max_temp
    self.pad_one = pad_one
    self.pad_two = pad_two
    self.pad_three = pad_three
    self.pad_four = pad_four
    self.pad_five = pad_five
    self.pad_six = pad_six
    self.rma = rma

class ModuleStatus(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  replaced_parts = db.Column(db.String)
  rma_id = db.Column(db.Integer, db.ForeignKey('rma.id'), nullable=False)
  rma = db.relationship('RMA', back_populates='module_status')

  def __init__(self, replaced_parts, rma):
    self.replaced_parts = replaced_parts
    self.rma = rma

class AccountSchema(ma.Schema):
    class Meta:
        fields = ('id', 'user_name', 'user_email', 'user_password_hash', 'user_auth')
account_schema = AccountSchema()
multi_account_schema = AccountSchema()

class VacStatusSchema(Schema):
    class Meta:
        fields = ('id', 'pump_type', 'pump_sn', 'pump_mtorr_1000', 'pump_mtorr_500', 'pump_mtorr_300', 'pump_mtorr_200', 'pump_mtorr_bo', 'mtorr_1000', 'mtorr_500', 'mtorr_300', 'mtorr_200', 'mtorr_bo')

vac_status_schema = VacStatusSchema()

class FreezeStatusSchema(Schema):
    class Meta:
        fields = ('id', 'coil_count', 'amp_reading', 'temp_front', 'temp_mid', 'temp_back')
    
freeze_status_schema = FreezeStatusSchema()

class HeatStatusSchema(Schema):
    class Meta:
        fields = ('id', 'ambient', 'heat_limit', 'max_temp', 'pad_one', 'pad_two', 'pad_three', 'pad_four', 'pad_five', 'pad_six')

heat_status_schema = HeatStatusSchema()

class ModuleStatusSchema(Schema):
    class Meta:
        fields = ('id', 'replaced_parts')

module_status_schema = ModuleStatusSchema()

class AccountSchema(Schema):
    class Meta:
        fields = ('id', 'user_name')

class RMASchema(Schema):
    vac_status = fields.Nested(VacStatusSchema)
    freeze_status = fields.Nested(FreezeStatusSchema)
    heat_status = fields.Nested(HeatStatusSchema)
    module_status = fields.Nested(ModuleStatusSchema)
    technician = fields.Nested(AccountSchema)
    
    class Meta:
        fields = ('id', 'odoo_id', 'fd_sn', 'bay', 'technician', 'repair_status', 'repair_notes', 'repair_parts', 'repair_completion', 'vac_status', 'freeze_status', 'heat_status', 'module_status')

rma_schema = RMASchema()
multi_rma_schema = RMASchema(many=True)


#***** Account Endpoints *****

    #Create
@app.route('/account/create', methods=["POST"])
def account_create():
  if request.content_type != 'application/json':
    return jsonify({"Error: JSONIFY"}), 400
  
  post_data = request.get_json()
  user_name = post_data.get('user_name')
  user_email = post_data.get('user_email')
  user_password_hash = post_data.get('user_password')
  user_auth = post_data.get('user_auth')
  if user_name == None:
    return jsonify({"Error: Username is required"}), 400
  if user_email == None:
    return jsonify({"Error: Email is required"}), 400
  
  if user_password_hash == None:
    return jsonify({"Error: Password is required"}), 400
  
  if user_auth == None:
    user_auth = 0
  try:
    hashed_password = generate_password_hash(user_password_hash)
    new_account = AccountInfo(user_name, user_email, hashed_password, user_auth)
    db.session.add(new_account)
    db.session.commit()
    return jsonify({'success': 'Account created successfully'})
  except exc.IntegrityError:
    db.session.rollback()
    return jsonify({'Error': 'Email already exists.'}), 400
  
    #Login
@app.route('/login', methods=["POST"])
def login():
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected JSON"}), 400

    email = request.json.get("user_email")
    password = request.json.get("user_password")
    user = db.session.query(AccountInfo).filter(AccountInfo.user_email == email).first()

    if user is None:
        return jsonify({'error': 'Invalid email'}), 401

    if not user.check_password(password):
        return jsonify({'error': 'Invalid password'}), 401

    expiration = datetime.utcnow() + timedelta(days=1)
    token_payload = {
       'user_id' : user.id,
       'exp': expiration,
    }

    jwt_token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({'id': user.id, 'token':jwt_token,'message': 'Login successful'}), 200

    #Get Account
@app.route('/accounts', methods=["GET"])
def get_accounts():
    all_accounts = db.session.query(AccountInfo).all()
    data = {
        "accounts": account_schema.dump(all_accounts, many=True)
    }
    return jsonify(data)

@app.route('/account/<id>', methods=["GET"])
def get_account(id):
    account = db.session.query(AccountInfo).get(id)
    if not account:
        return jsonify({"Error: Account not found"}), 404
    data = {
        "account": account_schema.dump(account),
    }
    return jsonify(data)


#*****RMA Endpoint*****

@app.route('/<id>/create_rma', methods=["POST"])
def rma_create(id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected JSON"}), 400

    data = request.get_json()

    odoo_id = data.get('odoo_id')
    fd_sn = data.get('fd_sn')
    bay = data.get('bay')
    repair_status = data.get('repair_status', '')
    repair_notes = data.get('repair_notes', '')
    repair_parts = data.get('repair_parts', '')
    repair_completion = data.get('repair_completion', False)

    technician = AccountInfo.query.get(id)

    if not technician:
        return jsonify({"error": f"Account with ID {id} not found"}), 404

    try:
        rma = create_rma(odoo_id, fd_sn, bay, technician.id, repair_status, repair_notes, repair_parts, repair_completion)

        vac_status_data = data.get('vac_status', {
          "pump_type": "",
          "pump_sn": "",
          "pump_mtorr_1000": 0,
          "pump_mtorr_500": 0,
          "pump_mtorr_300": 0,
          "pump_mtorr_200": 0,
          "pump_mtorr_bo": 0,
          "mtorr_1000": 0,
          "mtorr_500": 0,
          "mtorr_300": 0,
          "mtorr_200": 0,
          "mtorr_bo": 0
        })
        create_status(VacStatus, rma, vac_status_data)

        freeze_status_data = data.get('freeze_status', {
          "coil_count": "",
          "amp_reading": 0,
          "temp_front": 0,
          "temp_mid": 0,
          "temp_back": 0
        })
        create_status(FreezeStatus, rma, freeze_status_data)

        heat_status_data = data.get('heat_status', {
          "ambient": "",
          "heat_limit": 0,
          "max_temp": 0,
          "pad_one": 0,
          "pad_two": 0,
          "pad_three": 0,
          "pad_four": 0,
          "pad_five": 0,
          "pad_six": 0
        })
        create_status(HeatStatus, rma, heat_status_data)

        module_status_data = data.get('module_status', {"replaced_parts":""})
        create_status(ModuleStatus, rma, module_status_data)

        db.session.commit()

        serialized_rma = rma_schema.dump(rma)

        return jsonify({'success': 'RMA created successfully', 'data': serialized_rma})
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": f"Could not create RMA. {str(ve)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not create RMA. {str(e)}"}), 500

def create_rma(odoo_id, fd_sn, bay, technician_id, repair_status, repair_notes, repair_parts, repair_completion):
    rma = RMA(odoo_id, fd_sn, bay, technician_id, repair_status, repair_notes, repair_parts, repair_completion)
    db.session.add(rma)
    return rma

def create_status(status_model, rma, status_data):
    status = status_model(rma=rma, **status_data)
    db.session.add(status)
  
    #Delete All
@app.route('/rma/delete_all', methods=['DELETE'])
def delete_all_rmas():
  try:
    db.session.query(RMA).delete()
    db.session.commit()

    return jsonify({'success': 'All RMAs deleted successfully'})
  except Exception as e:
    db.session.rollback()
    return jsonify({'error': f'Failed to delete all RMAs. {str(e)}'}), 500
  finally:
    db.session.close()
      #Get
@app.route('/account/<technician_id>/rmas', methods=['GET'])
def get_technician_rmas(technician_id):
  try:
    rmas = RMA.query.filter_by(technician_id=technician_id).all()

    serialized_rmas = multi_rma_schema.dump(rmas)

    return jsonify({'data': serialized_rmas})
  except Exception as e:
    return jsonify({'error': f'Failed to retrieve RMAs. {str(e)}'}), 500

@app.route('/manager/rmas', methods=['GET'])
def get_all_rmas():
  try:
    all_rmas = RMA.query.all()

    serialized_rmas = multi_rma_schema.dump(all_rmas)

    return jsonify({'data': serialized_rmas})
  except Exception as e:
    return jsonify({'error': f'Failed to retrieve RMAs. {str(e)}'}), 500
  
@app.route('/rmas', methods=['GET'])
def get_specific_rmas():
    try:
        odoo_id = request.args.get('odoo_id')
        repair_status = request.args.get('repair_status')

        query = RMA.query

        if odoo_id:
            query = query.filter_by(odoo_id=odoo_id)

        if repair_status:
            query = query.filter_by(repair_status=repair_status)

        specific_rmas = query.all()

        serialized_rmas = multi_rma_schema.dump(specific_rmas)

        return jsonify({'data': serialized_rmas})
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve RMAs. {str(e)}'}), 500
    
@app.route('/rma/<id>', methods=["GET"])
def get_rma(id):
    rma = db.session.query(RMA).get(id)
    if not rma:
        return jsonify({"Error: RMA not found"}), 404
    data = rma_schema.dump(rma)
    return jsonify(data)
    
#*****Status Enpoints*****
    #GET
@app.route('/rma/<rma_id>/get_freeze_status', methods=["GET"])
def get_freeze_status(rma_id):
    try:
        rma = RMA.query.get(rma_id)

        if not rma:
            return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

        freeze_status = FreezeStatus.query.filter_by(rma_id=rma_id).first()

        if not freeze_status:
            return jsonify({"error": f"FreezeStatus for RMA with ID {rma_id} not found"}), 404

        serialized_freeze_status = freeze_status_schema.dump(freeze_status)
        return jsonify({'data': serialized_freeze_status})

    except Exception as e:
        return jsonify({"error": f"Failed to get freeze status. {str(e)}"}), 500
    
@app.route('/rma/<rma_id>/get_heat_status', methods=["GET"])
def get_heat_status(rma_id):
    try:
        rma = RMA.query.get(rma_id)

        if not rma:
            return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

        heat_status = HeatStatus.query.filter_by(rma_id=rma_id).first()

        if not heat_status:
            return jsonify({"error": f"HeatStatus for RMA with ID {rma_id} not found"}), 404

        serialized_heat_status = heat_status_schema.dump(heat_status)
        return jsonify({'data': serialized_heat_status})

    except Exception as e:
        return jsonify({"error": f"Failed to get heat status. {str(e)}"}), 500
    
@app.route('/rma/<rma_id>/get_vac_status', methods=["GET"])
def get_vac_status(rma_id):
    try:
        rma = RMA.query.get(rma_id)

        if not rma:
            return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

        vac_status = VacStatus.query.filter_by(rma_id=rma_id).first()

        if not vac_status:
            return jsonify({"error": f"VacStatus for RMA with ID {rma_id} not found"}), 404

        serialized_vac_status = vac_status_schema.dump(vac_status)
        return jsonify({'data': serialized_vac_status})

    except Exception as e:
        return jsonify({"error": f"Failed to get Vac status. {str(e)}"}), 500
    
@app.route('/rma/<rma_id>/get_module_status', methods=["GET"])
def get_module_status(rma_id):
    try:
        rma = RMA.query.get(rma_id)

        if not rma:
            return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

        module_status = ModuleStatus.query.filter_by(rma_id=rma_id).first()

        if not module_status:
            return jsonify({"error": f"ModuleStatus for RMA with ID {rma_id} not found"}), 404

        serialized_module_status = module_status_schema.dump(module_status)
        return jsonify({'data': serialized_module_status})

    except Exception as e:
        return jsonify({"error": f"Failed to get Module status. {str(e)}"}), 500
    
    #PUT
@app.route('/rma/<rma_id>/update_vac_status', methods=["PUT"])
def update_vac_status(rma_id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected JSON"}), 400
    
    data = request.get_json()
    vac_status_data = data.get('data')

    rma = RMA.query.get(rma_id)

    if not rma:
        return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

    try:
        vac_status = VacStatus.query.filter_by(rma_id=rma_id).first()

        if not vac_status:
            vac_status = VacStatus(rma=rma, **vac_status_data)
            db.session.add(vac_status)
        else:
            for key, value in vac_status_data.items():
                setattr(vac_status, key, value)

        db.session.commit()

        serialized_vac_status = vac_status_schema.dump(vac_status)

        return jsonify({'success': 'VacStatus updated successfully', 'data': serialized_vac_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not update VacStatus. {str(e)}"}), 500
    
@app.route('/rma/<rma_id>/update_freeze_status', methods=["PUT"])
def update_freeze_status(rma_id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected JSON"}), 400
    
    data = request.get_json()
    freeze_status_data = data.get('data')

    rma = RMA.query.get(rma_id)

    if not rma:
        return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

    try:
        freeze_status = FreezeStatus.query.filter_by(rma_id=rma_id).first()

        if not freeze_status:
            freeze_status = FreezeStatus(rma=rma, **freeze_status_data)
            db.session.add(freeze_status)
        else:
            for key, value in freeze_status_data.items():
                setattr(freeze_status, key, value)

        db.session.commit()

        serialized_freeze_status = freeze_status_schema.dump(freeze_status)

        return jsonify({'success': 'freezeStatus updated successfully', 'data': serialized_freeze_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not update freezeStatus. {str(e)}"}), 500
    
@app.route('/rma/<rma_id>/update_heat_status', methods=["PUT"])
def update_heat_status(rma_id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected JSON"}), 400

    data = request.get_json()
    heat_status_data = data.get('data')

    rma = RMA.query.get(rma_id)

    if not rma:
        return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

    try:
        heat_status = HeatStatus.query.filter_by(rma_id=rma_id).first()

        if not heat_status:
            heat_status = HeatStatus(rma=rma, **heat_status_data)
            db.session.add(heat_status)
        else:
            for key, value in heat_status_data.items():
                setattr(heat_status, key, value)

        db.session.commit()

        serialized_heat_status = heat_status_schema.dump(heat_status)

        return jsonify({'success': 'heatStatus updated successfully', 'data': serialized_heat_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not update heatStatus. {str(e)}"}), 500
    
@app.route('/rma/<rma_id>/update_module_status', methods=["PUT"])
def update_module_status(rma_id):
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected JSON"}), 400

    data = request.get_json()
    module_status_data = data.get('module_status', {})

    rma = RMA.query.get(rma_id)

    if not rma:
        return jsonify({"error": f"RMA with ID {rma_id} not found"}), 404

    try:
        module_status = ModuleStatus.query.filter_by(rma_id=rma_id).first()

        if not module_status:
            module_status = ModuleStatus(rma=rma, **module_status_data)
            db.session.add(module_status)
        else:
            for key, value in module_status_data.items():
                setattr(module_status, key, value)

        db.session.commit()

        serialized_module_status = module_status_schema.dump(module_status)

        return jsonify({'success': 'moduleStatus updated successfully', 'data': serialized_module_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Could not update moduleStatus. {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)