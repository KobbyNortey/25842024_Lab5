import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify

app = Flask(__name__)

# initialize Firestore
cred = credentials.Certificate("lab-4-382620-515382ca7284.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Registering a student as a voter
@app.route('/register-voter', methods=['POST'])
def register_voter():
    record = json.loads(request.data)
    voters_ref = db.collection(u'voters')
    existing_voter = voters_ref.where(u'ID', u'==', record['ID']).get()
    if existing_voter:
        return jsonify({"error" : "Voter already exists"})
    else:
        voters_ref.add(record)
        return jsonify(record)

# Updating a Registered Voter's Information
@app.route('/update_voter/<id>',methods=['PUT'])               
def update_voter(id):
    if not request.data:
        return jsonify({"error": "no data has been entered"})
    
    voters_ref = db.collection(u'voters')
    voter_doc = voters_ref.document(id)
    if voter_doc.get().exists:
        voter_doc.update(request.json)
        return jsonify(voter_doc.get().to_dict())
    else:
        return jsonify({"error": "student not found"}), 404

# De-registering a Student as a Voter
@app.route('/voter/<id>', methods=['DELETE'])
def deregister_voter(id):
    voters_ref = db.collection(u'voters')
    voter_doc = voters_ref.document(id)
    if voter_doc.get().exists:
        voter_doc.delete()
        return jsonify(voter_doc.get().to_dict())
    else:
        return jsonify({"error":"student not found"}), 404

# Retrieving a registered voter
@app.route('/retrieve-voter', methods=['GET'])
def retrieve_voter():
    student = json.loads(request.data)
    voters_ref = db.collection(u'voters')
    existing_voter = voters_ref.where(u'ID', u'==', student['ID']).get()
    if existing_voter:
        voter = existing_voter[0].to_dict()
        return jsonify({
            'id': voter['ID'],
            'name': voter['name'],
            'major': voter['major'],
            'class': voter['class']
        })
    else:
        return jsonify({"error": "student not found"}), 404

# Creating an Election
@app.route('/create_election', methods=['POST'])
def create_election():
    record = json.loads(request.data)
    election_ref = db.collection(u'elections')
    existing_election = election_ref.where(u'electionID', u'==', record['electionID']).get()
    if existing_election:
        return jsonify({"error" : "Election already exists"})
    else:
        election_ref.add(record)
        return jsonify(record)

# Voting in an Election
@app.route('/election/<electionid>/<candidateid>', methods = ['PATCH'])
def vote_election(electionid,candidateid):
    election_ref = db.collection(u'elections')
    candidate_doc = election_ref.document(electionid).collection(u'candidates').document(candidateid)
    if candidate_doc.get().exists:
        candidate_doc.update({
            u'votesCast': firestore.Increment(1)
        })
        election_doc = election_ref.document(electionid)
        return jsonify(election_doc.get().to_dict())
    else:
        return jsonify({"error": "candidate not found"}), 404

#Deleting an election
@app.route('/delete_election/<id>', methods=['DELETE'])
def delete_election(id):
    election_ref = db.collection('elections').document(id)
    election_doc = election_ref.get()
    if not election_doc.exists:
        return jsonify({"error":"election not found"}), 404
    else:
        election_ref.delete()
        return jsonify({"message": "election deleted successfully"})


# Retrieving an Election
@app.route('/retrieve_election/<id>', methods=['GET'])
def retrieve_election(id):
    election_ref = db.collection('elections').document(id)
    election_doc = election_ref.get()
    if not election_doc.exists:
        return jsonify({"error": "election not found"}), 404
    else:
        election_data = election_doc.to_dict()
        return jsonify(election_data)




app.run(debug=True)