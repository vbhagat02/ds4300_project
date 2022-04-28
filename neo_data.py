
from py2neo import Graph, Node, Relationship
import pymongo
import json
import random as rnd
from bson.json_util import dumps


def load_data(filename):
    with open(filename) as file:
        j = json.load(file)
    return j


class NeoApp:

    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def execute_query(self, query):
        """returns a list of results"""
        return self.graph.query(query).data()

    def clear_database(self):
        """Clear all nodes and relationships"""
        self.graph.delete_all()

    def create_node(self, label, **kwargs):
        """Create a new node, and none or many properties associated with that node"""
        tx = self.graph.begin()
        nod = Node(label, **kwargs)
        tx.create(nod)
        self.graph.commit(tx)
        return nod

    def create_relationship(self, n1, label, n2, **kwargs):
        """Create a new relationship b/w 2 nodes, and none or many properties associated with that relationship"""
        tx = self.graph.begin()
        rel = Relationship(n1, label, n2, **kwargs)
        tx.create(rel)
        self.graph.commit(tx)
        return rel

    def show_full_database(self):
        """Show all nodes and relationships in the database"""
        query = """MATCH (n) RETURN n"""
        return self.execute_query(query)

    def if_exists(self, subgraph):
        return self.graph.exists(subgraph)

    def graph_match(self, nodes=None, rels=None, limit=None):
        """Run a match query"""
        return self.graph.match(nodes, rels, limit)

    def create_data(self):
        """Created randomly generated data to initialize database"""
        names = ["Brandon", "Sarah", "Vedant", "Kreena", "Deeptha", "Rachlin"]
        mails = [name.lower() + "@neu.edu" for name in names]
        dobs = []

        streets = [str(rnd.randrange(1000)) +
                   " Huntington Ave" for _ in range(100)]  # 100 listings
        beds = [str(rnd.randrange(1, 5))
                for _ in range(len(streets))]  # 0-4 beds
        baths = [str(rnd.randrange(1, 4))
                 for _ in range(len(streets))]  # 0-3 baths
        price = [str(rnd.randrange(1000, 3000, 100))
                 for _ in range(len(streets))]  # $1000-$3000

        user_nodes = []
        listing_nodes = []
        rels = set()
        for i in range(len(names)):
            n = self.create_node(
                "User", user_id=names[i], name=names[i], email=mails[i], dob="01/01/2001")
            user_nodes.append(n)

        for i in range(len(streets)):
            n = self.create_node("Listing", listing_id=streets[i], address=streets[i], city="Boston", state="MA", zip="02115", bed=beds[i],
                                 bath=baths[i], price=price[i])
            listing_nodes.append(n)

        while len(rels) < 100:  # generate 100 random relationships
            i, j = rnd.randrange(len(user_nodes)), rnd.randrange(
                len(listing_nodes))
            if (i, j) not in rels:
                u, t = user_nodes[i], listing_nodes[j]
                self.create_relationship(u, "Likes", t, strength="1")
            rels.add((i, j))

    def recommend_listings(self, name, feat="name", num_recommendations=4):
        """
        Make {num_recommendations} listing recommendations for a user.
        Find the 3 most similar users, defined by those with the largest number of commonly liked listings.
        Then, take all listings those users like that specified user doesn't, and return the 4 (num_recommendations)
        listings from that list that have the most users liking it.
        """
        feat1, name1 = feat, name
        num = num_recommendations
        form_name = "{" + "{}: {}".format(feat1, "\"" + name1 + "\"") + "}"
        q = """MATCH (n: User {0})-[r: Likes]->(t: Listing)<-[r2: Likes]-(n2: User)
            WHERE n <> n2
            WITH n, n2, COUNT(DISTINCT t) as common 

            ORDER BY common DESC LIMIT 3
            WITH n, COLLECT(n2) as closest
            UNWIND closest as close
            WITH n, close

            MATCH (close)-[r3: Likes]->(t: Listing)<-[r4: Likes]-(n3: User)
            WHERE not (n)-[]->(t)
            WITH n, t, COUNT(DISTINCT r4) as others
            ORDER BY others DESC LIMIT {1}
            RETURN COLLECT(DISTINCT t) as recommendations
            """.format(form_name, num)
        result = self.execute_query(q)
        return result

    def recommend_users(self, name, feat="name", num_recommendations=4):
        """Make {num_recommendations} user recommendations for a user. Find the 3 (num_recommendations)
        most similar users, defined by those with the largest number of commonly liked listings."""
        feat1, name1 = feat, name
        num = num_recommendations
        form_name = "{" + "{}: {}".format(feat1, "\"" + name1 + "\"") + "}"

        q = """MATCH (n: User {0})-[r: Likes]->(t: Listing)<-[r2: Likes]-(n2: User)
            WHERE n <> n2
            WITH n, n2, COUNT(DISTINCT t) as common 

            ORDER BY common DESC LIMIT 3
            RETURN n, COLLECT(n2) as closest
            """.format(form_name, num)
        result = self.execute_query(q)
        return result


def load_to_json(coll, filename):
    cursor = coll.find({})
    with open(filename, 'w') as file:
        json.dump(json.loads(dumps(cursor)), file)


def insert_user(name, email, dob, username, password, user_id=None):
    """ replace 'housing' with name of database once created """
    client = pymongo.MongoClient()
    collection = client.finalproject.users

    # check if id in database
    if user_id == None:
        user_id = rnd.randrange(1000)

    if collection.find_one({"user_id":  user_id}):
        update_user(user_id, name, email, dob, username, password)
    else:
        data_dict = {"user_id": user_id, "name": name, "email": email,
                     "dob": dob, 'username': username, 'password': password}
        collection.insert_one(data_dict)
    client.close()


def insert_listing(street, city, state, zip, bed, bath, rent, listing_id=None, uid=None):
    client = pymongo.MongoClient("mongodb://localhost")
    listings_col = client.finalproject.listings
    # check if id in database

    if listing_id == None:
        listing_id = rnd.randrange(10000)

    if uid == None:
        uid = rnd.randrange(100)  # user that posted

    if listings_col.find_one({"listing_id": listing_id}):
        update_listing(listing_id, uid, street, city,
                       state, zip, bed, bath, rent)
    else:
        listing = {'listing_id': listing_id,
                   'user_id': uid,
                   'address':
                       {'street': street,
                        'city': city,
                        'state': state,
                        'zip code': zip},
                   'details': {
                       'bedrooms': bed,
                       'bathrooms': bath
                       },
                   'rent': rent}
        listings_col.insert_one(listing)
    client.close()


def insert_likes(user_id, listing_id, relat, strength):
    """ replace 'housing' with name of database once created """
    client = pymongo.MongoClient()
    likes_collection = client.finalproject.likes

    # check if id in database
    relat_id = rnd.randrange(100000)
    if not likes_collection.find_one({"relat_id":  relat_id}):
        data_dict = {"user": user_id, "listing": listing_id,
                     "relat": relat, "strength": strength}
        likes_collection.insert_one(data_dict)
    client.close()


def delete_listing(listing_id):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.listings
    col.delete_one({"listing id": listing_id})
    client.close()


def delete_user(user_id):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.users
    col.delete_one({"user_id": user_id})
    client.close()


def update_listing(listing_id, uid, street, city, state, zip, bed, bath, rent):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.listings
    listing = {'listing_id': listing_id,
               'user_id': uid,
               'address':
                   {'street': street,
                    'city': city,
                    'state': state,
                    'zip code': zip},
               'details': {
                   'bedrooms': bed,
                   'bathrooms': bath},
               'rent': rent}
    col.replace_one({"user_id": listing_id}, listing)
    # col.findOneAndReplace({"listing_id": listing_id}, listing)
    client.close()


def update_user(user_id, name, email, dob, username, password):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.users
    user_info = {"user_id": user_id,
                 "name": name,
                 "email": email,
                 "dob": dob,
                 "username": username,
                 "password": password
                 }

    col.replace_one({"user_id": user_id}, user_info)
    # col.findOneAndReplace({"user_id": user_id}, user_info)
    client.close()


def reset_mongo():
    client = pymongo.MongoClient("mongodb://localhost")
    client.finalproject.users.drop()
    client.finalproject.listings.drop()
    client.finalproject.likes.drop()

    for user in load_data("user.json"):
        insert_user(user["name"], user["email"],
                    user["dob"], "username", "password")

    for listing in load_data("listing.json"):
        insert_listing(listing["address"]["street"], listing["address"]["city"], listing["address"]["state"],
                       listing["address"]["zip code"], listing["details"]["bedrooms"], listing["details"]["bathrooms"],
                       listing["rent"])

    for relat in load_data("relats.json"):
        insert_likes(relat["user"], relat["listing"],
                     relat["relat"], relat["strength"])


def load_mongo_to_neo(client, g):
    g.clear_database()
    load_to_json(client.finalproject.users, "user.json")
    user_nodes = []

    for user in load_data("user.json"):
        n = g.create_node("User", user_id=user["user_id"], name=user["name"], email=user["email"], dob=user["dob"],
                          username="username", password="password")
        user_nodes.append(n)

    load_to_json(client.finalproject.listings, "listing.json")
    listing_nodes = []

    for listing in load_data("listing.json"):
        n = g.create_node("Listing", listing_id=listing["listing_id"], address=listing["address"]["street"],
                          city=listing["address"]["city"], state=listing["address"]["state"],
                          zip=listing["address"]["state"],
                          bed=listing["details"]["bedrooms"], bath=listing["details"]["bathrooms"],
                          price=listing["rent"])
        listing_nodes.append(n)

    load_to_json(client.finalproject.likes, "relats.json")
    rels = set()
    for relat in load_data("relats.json"):
        user1, list1 = relat["user"], relat["listing"]
        for n1 in user_nodes:
            for n2 in listing_nodes:
                if n1["name"] == user1 and n2["address"] == list1:
                    g.create_relationship(
                        n1, relat["relat"], n2, strength=relat["strength"])
                    rels.add((n1, n2))
    return


def load_neo_to_mongo(client, g):
    r1 = g.execute_query("""MATCH (n: User) RETURN n""")
    r2 = g.execute_query("""MATCH (n2: Listing) RETURN n2""")
    r3 = g.execute_query(
        """MATCH (n: User)-[r1: Likes]->(t: Listing) RETURN r1""")

    # load users into mongo
    for user_id, name, email, dob, user, passw in [(d["n"]['user_id'], d["n"]['name'], d["n"]['email'], d["n"]['dob'], d["n"]['username'], d["n"]['password']) for d in r1]:
        insert_user(name, email, dob, user, passw, user_id=user_id)

    # load listings into mongo
    for listing_id, address, city, state, zip, bath, bed, price in [(d["n2"]['listing_id'], d["n2"]['address'], d["n2"]['city'], d["n2"]['state'], d["n2"]['zip'], d["n2"]['bath'], d["n2"]['bed'], d["n2"]['price']) for d in r2]:
        insert_listing(address, city, state, zip, bed,
                       bath, price, listing_id=listing_id)

    # load relationships into mongo
    for user_id, listing_id, strength in [(d['r1'].start_node["user_id"], d['r1'].end_node["listing_id"], d['r1']['strength']) for d in r3]:
        print(user_id, listing_id)
        insert_likes(user_id, listing_id, "Likes", strength)
    print('done')


def main():
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "neo4jj"

    g = NeoApp(uri, user, password)
    client = pymongo.MongoClient()

    reset_mongo()
    # g.clear_database()
    # g.create_data()

    load_mongo_to_neo(client, g)  # load data from mongo to neo4j

    # res = g.show_full_database()
    person = "Rachlin"
    print(f"Recommendations for {person}...")

    print("\nRecommended listings:")
    res2 = g.recommend_listings(person)
    for r in res2[0]['recommendations']:
        print(r)
    print(f"Number of recommended listings: {len(res2[0]['recommendations'])}")

    print("\nRecommended Users:")
    res3 = g.recommend_users(person)
    for r in res3[0]['closest']:
        print(r)
    print(f"Number of recommended users: {len(res3[0]['closest'])}")

    load_neo_to_mongo(client, g)  # load data from neo4j to mongo

    # insert_user('John Doe', 'doe.j@northeastern.edu', '04/03/2001')
    # insert_listing('360 Huntington Ave', 'Boston', 'MA', '02115', '1', '1', '1600')


if __name__ == "__main__":
    main()
