conn = new Mongo();
db = conn.getDB("docai-db");

db.createCollection('document');
db.createCollection('results');
db.createCollection('users');

db.createUser(
    {
        user: "edwin",
        pwd: "cheong-25",
        roles: [
            {
                role: "readWrite",
                db: "docai-db"
            }
        ]
    }
);