import pymongo
from pymongo import MongoClient, InsertOne

# client = pymongo.MongoClient("mongodb://localhost")
# db = client.finalproject
# users_col = db.users


def insert_user(name, email, dob, username, password):
    """ replace 'housing' with name of database once created """
    client = pymongo.MongoClient("mongodb://localhost")
    users_col = client.finalproject.users

    data_dict = {}
    data_dict["name"] = name
    data_dict["email"] = email
    data_dict["dob"] = dob
    data_dict['username'] = username
    data_dict['password'] = password

    users_col.insert_one(data_dict)
    client.close()


def insert_listing(uid, listing_id, street, city, state, zip, bed, bath, rent):
    client = pymongo.MongoClient("mongodb://localhost")
    listings_col = client.finalproject.listings
    listing = {'user_id': uid,
               'listing_id': listing_id,
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


def get_user(email):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.users
    user = col.find_one({"email": email})
    client.close()
    return user


def update_listing(listing_id, uid, street, city, state, zip, bed, bath, rent):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.listings
    listing = {'user_id': uid,
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
    col.findOneAndUpdate({"listing id": listing_id}, listing)
    client.close()


def update_user(user_id, name, email, dob, username, password):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.users
    user_info = {"name": name,
                 "email": email,
                 "dob": dob,
                 "username": username,
                 "password": password
                 }
    col.findOneAndUpdate({"user_id": user_id}, user_info)
    client.close()


def delete_listing(listing_id):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.listings
    col.delete_one({"listing id": listing_id})
    client.close()


def delete_user(user_id):
    client = pymongo.MongoClient("mongodb://localhost")
    col = client.finalproject.users
    client.delete_one({"user_id": user_id})
    client.close()


if __name__ == "__main__":
    insert_user('Vedant Bhagat', 'vedant.bhagat0204@gmail.com', '04/02/2002')
    insert_listing('9 Mission St', 'Boston', 'MA', '02115', '4', '2', '1160')
    insert_user('Sarah Costa', 'sarah_costa@gmail.com', '01/01/2002')
    insert_listing('52 Westland Ave', 'Boston',
                   'MA', '02115', '4', '1', '1600')
