# ----------------------------------------------------------------------
# Name:        business_reviews
# Purpose:     An application which features crowd-sourced reviews for
#              businesses. Users can sign up to search for businesses
#              ranging from restaurants to barbershops. They can view
#              the specific services businesses offer as well as reviews
#              of the business. Users can also leave their own reviews
#              of businesses using a five star rating system.
#
# Authors: Kenny Nguyen, Richard Ma, Brandon Palomino
# ----------------------------------------------------------------------
from pymongo import MongoClient
from datetime import date
import random
import string
import re


def main_menu(db):
    choice = True
    while choice:
        print(f"{25 * '='} MAIN MENU {25 * '='}")
        print("Welcome to the Business Reviews System!\n"
              "To begin, please login or create an account.\n"
              "[1] = Login\n"
              "[2] = Register\n"
              "[0] = Exit")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            login(db)
        elif choice == '2':
            register(db)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


def login(db):
    print(f"{27 * '='} LOGIN {27 * '='}")
    name = input("Enter username: ")
    password = input("Enter password: ")
    user_count = db.user.count_documents({"name": name, "password": password})
    user = db.user.find_one({"name": name, "password": password})
    if user_count:
        print(f"Hi {user['name']}, you are now logged in!\n")
        initial_choices(db, user["user_id"])
    else:
        print("Incorrect username or password. Please try again.\n")


# Query 1: Create an account
def register(db):
    print(f"{25 * '='} REGISTER {25 * '='}")
    user_id = generate_id()
    name = input("Enter a username: ")
    password = input("Enter a password: ")
    creation_date = str(date.today())
    registered = db.user.insert_one({"user_id": user_id, "name": name,
                                     "password": password,
                                     "yelping_since": creation_date,
                                     "review_count": 0,
                                     "useful": 0, "funny": 0, "cool": 0,
                                     "fans": 0,
                                     "average_stars": 0})
    if registered.inserted_id:
        print("Account successfully created! Please login...\n")
        login(db)
    else:
        print("An error occurred. Please try again.\n")


def initial_choices(db, user_id):
    choice = True
    while choice:
        print(f"{18 * '='} BUSINESS REVIEWS SYSTEM {18 * '='}")
        print("[1] = Search\n"
              "[2] = View\n"
              "[3] = My Reviews\n"
              "[0] = Logout")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            search_prompt(db, user_id)
        elif choice == '2':
            view_prompt(db, user_id)
        elif choice == '3':
            review_prompt(db, user_id)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


def search_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{26 * '='} SEARCH {27 * '='}")
        print("[1] = Search Businesses\n"
              "[2] = Search Users\n"
              "[0] = Return")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            search_business_prompt(db, user_id)
        elif choice == '2':
            search_users(db)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


def search_business_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{21 * '='} SEARCH BUSINESSES {21 * '='}")
        print("[1] = Search By City & State\n"
              "[2] = Search By Zipcode\n"
              "[0] = New Search")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            search_business_by_city_state(db, user_id)
        elif choice == '2':
            search_business_by_zipcode(db, user_id)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 2: Search for business by city
def search_business_by_city_state(db, user_id):
    city = input("Enter a city: ")
    state = input("Enter a state abbreviation: ")
    print()
    search_business_by_attributes_prompt(db, user_id, city=city, state=state)


# Query 3: Search for business by zip code
def search_business_by_zipcode(db, user_id):
    zipcode = input("Enter a zipcode: ")
    print()
    search_business_by_attributes_prompt(db, user_id, zipcode=zipcode)


def search_business_by_attributes_prompt(db, user_id, **kwargs):
    choice = True
    while choice:
        print(f"{21 * '='} CHOOSE ATTRIBUTE {22 * '='}")
        print("[1] = Search By Name\n"
              "[2] = Search By Category\n"
              "[3] = Search By Rating\n"
              "[0] = New Search")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            search_business_by_name(db, user_id, **kwargs)
        elif choice == '2':
            search_business_by_category(db, user_id, **kwargs)
        elif choice == '3':
            search_business_by_rating(db, user_id, **kwargs)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 4: Search for business by name
def search_business_by_name(db, user_id, **kwargs):
    name = input("Enter a name: ")
    print()
    regex = re.compile(name, re.IGNORECASE)
    if "city" in kwargs.keys() and "state" in kwargs.keys():
        businesses_count = db.business.count_documents({"state": kwargs.get(
            "state"),
            "city": kwargs.get("city"),
            "name": {"$regex": regex}})
        businesses = db.business.find({"state": kwargs.get("state"),
                                       "city": kwargs.get("city"),
                                       "name": {"$regex": regex}})
    else:
        businesses_count = db.business.count_documents(
            {"postal_code": kwargs.get("zipcode"),
             "name": {"$regex": regex}})
        businesses = db.business.find({"postal_code": kwargs.get("zipcode"),
                                       "name": {"$regex": regex}})

    if businesses_count:
        for business in businesses:
            display_business(business)
        view_or_create_reviews_prompt(db, user_id)
    else:
        print("No businesses found. Try a different search!\n")


# Query 5: Search for business by category
def search_business_by_category(db, user_id, **kwargs):
    category = input("Enter a category: ")
    print()
    regex = re.compile(category, re.IGNORECASE)
    if "city" in kwargs.keys() and "state" in kwargs.keys():
        businesses_count = db.business.count_documents(
            {"state": kwargs.get("state"),
             "city": kwargs.get("city"),
             "categories": {"$regex": regex}})
        businesses = db.business.find({"state": kwargs.get("state"),
                                       "city": kwargs.get("city"),
                                       "categories": {"$regex": regex}})
    else:
        businesses_count = db.business.count_documents(
            {"postal_code": kwargs.get("zipcode"),
             "categories": {"$regex": regex}})
        businesses = db.business.find({"postal_code": kwargs.get("zipcode"),
                                       "categories": {"$regex": regex}})

    if businesses_count:
        for business in businesses:
            display_business(business)
        view_or_create_reviews_prompt(db, user_id)
    else:
        print("No businesses found. Try a different search!\n")


# Query 6: Search for business by rating
def search_business_by_rating(db, user_id, **kwargs):
    rating = ""
    while True:
        try:
            rating = float(input("Enter a rating: "))
            print()
            break
        except ValueError:
            print("Please input a number...")
            continue

    if "city" in kwargs.keys() and "state" in kwargs.keys():
        businesses_count = db.business.count_documents(
            {"state": kwargs.get("state"),
             "city": kwargs.get("city"),
             "stars": rating})
        businesses = db.business.find({"state": kwargs.get("state"),
                                       "city": kwargs.get("city"),
                                       "stars": rating})
    else:
        businesses_count = db.business.count_documents(
            {"postal_code": kwargs.get("zipcode"),
             "stars": rating})
        businesses = db.business.find({"postal_code": kwargs.get("zipcode"),
                                       "stars": rating})

    if businesses_count:
        for business in businesses:
            display_business(business)
        view_or_create_reviews_prompt(db, user_id)
    else:
        print("No businesses found. Try a different search!\n")


# Query 7: Search for users
def search_users(db):
    name = input("Enter a name: ")
    users_count = db.user.count_documents({"name": name})
    if users_count:
        users = db.user.find({"name": name})
        for user in users:
            display_user(user)
    else:
        print("No users found. Try a different search!\n")


def view_or_create_reviews_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{20 * '='} VIEW OR CREATE REVIEWS {20 * '='}")
        print("[1] = View A Business's Reviews\n"
              "[2] = Give A Review\n"
              "[0] = New Search")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            view_business_reviews_prompt(db)
        elif choice == '2':
            create_user_review(db, user_id)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


def view_business_reviews_prompt(db):
    not_valid_business = True
    business_id = ""
    while not_valid_business:
        business_id = input("Enter a business id: ")
        business = get_business(db, business_id)
        if business:
            not_valid_business = False
            print()
        else:
            print("No business found. Try a different search!\n")

    choice = True
    while choice:
        print(f"{15 * '='} VIEW {business['name']}'s REVIEWS {15 * '='}")
        print("[1] = View All Reviews\n"
              "[2] = View Most Useful Review\n"
              "[3] = View Funniest Review\n"
              "[4] = View Coolest Review\n"
              "[0] = Return")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            view_all_business_reviews(db, business_id)
        elif choice == '2':
            view_most_useful_business_review(db, business_id)
        elif choice == '3':
            view_funniest_business_review(db, business_id)
        elif choice == '4':
            view_coolest_business_review(db, business_id)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 12: View a business's reviews
def view_all_business_reviews(db, business_id):
    reviews = db.review.find({"business_id": business_id})
    for review in reviews:
        display_review(db, review)
        print("----------------------------------------\n")


# Query 13: View most useful review of a business
def view_most_useful_business_review(db, business_id):
    reviews = db.review.find({"business_id": business_id}).sort("useful",
                                                                -1).limit(1)
    for review in reviews:
        display_review(db, review)


# Query 14: View funniest review of a business
def view_funniest_business_review(db, business_id):
    reviews = db.review.find({"business_id": business_id}).sort("funny",
                                                                -1).limit(1)
    for review in reviews:
        display_review(db, review)


# Query 15: View coolest review of a business
def view_coolest_business_review(db, business_id):
    reviews = db.review.find({"business_id": business_id}).sort("cool",
                                                                -1).limit(1)
    for review in reviews:
        display_review(db, review)


def view_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{27 * '='} VIEW {27 * '='}")
        print("[1] = View My Profile\n"
              "[2] = View Top 10 Businesses\n"
              "[3] = View Most Reviewed Businesses\n"
              "[4] = View Most Prolific Reviewer\n"
              "[5] = View Harshest Critic\n"
              "[0] = Return")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            view_user_profile(db, user_id)
        elif choice == '2':
            view_top_rated_businesses(db)
        elif choice == '3':
            view_most_rated_businesses(db)
        elif choice == '4':
            view_user_most_reviews(db)
        elif choice == '5':
            view_user_lowest_average_rating(db)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 11: View your account profile
def view_user_profile(db, user_id):
    user = db.user.find_one({"user_id": user_id})
    display_user(user)


# Query 8: View top 10 businesses
def view_top_rated_businesses(db):
    businesses = db.business.find({"stars": 5,
                                   "review_count": {"$gte": 100}}).sort(
        "stars", -1).limit(10)
    for count, business in enumerate(businesses):
        print("#" + str(count + 1))
        display_business(business)


# Query 9: View most reviewed business
def view_most_rated_businesses(db):
    businesses = db.business.find().sort("review_count", -1).limit(1)
    for business in businesses:
        display_business(business)


# Query 16: View user with the most reviews
def view_user_most_reviews(db):
    users = db.user.find().sort("review_count", -1).limit(1)
    for user in users:
        display_user(user)


# Query 17: View user that is the harshest critic
def view_user_lowest_average_rating(db):
    users = db.user.find({"review_count": {"$gt": 100},
                          "average_stars": {"$exists": True}}).sort(
        "average_stars", 1).limit(1)
    for user in users:
        display_user(user)


def review_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{25 * '='} MY REVIEWS {24 * '='}")
        print("[1] = View My Reviews\n"
              "[2] = Make A Review\n"
              "[3] = Update A Review\n"
              "[4] = Delete A Review\n"
              "[0] = Return")
        choice = input("Enter your choice: ")
        print()
        if choice == '1':
            view_user_reviews(db, user_id)
        elif choice == '2':
            create_user_review(db, user_id)
        elif choice == '3':
            update_user_review(db, user_id)
        elif choice == '4':
            delete_user_review(db, user_id)
        elif choice == '0':
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 10: View all reviews made by your account
def view_user_reviews(db, user_id):
    reviews = db.review.find({"user_id": user_id})
    if reviews:
        for review in reviews:
            display_review(db, review)
    else:
        print("You haven't made any reviews!\n")


# Query 18: Create a review for a business
def create_user_review(db, user_id):
    business_id = input("Enter a Business ID: ")
    business = get_business(db, business_id)
    if business:
        stars = 0
        while stars < 1 or stars > 5:
            stars = int(input("Rate this business (1 - 5): "))
        text = input("Write your review: ")
        review_id = generate_id()
        review_date = str(date.today())
        created = db.review.insert_one({"review_id": review_id,
                                        "user_id": user_id,
                                        "business_id": business_id,
                                        "stars": stars,
                                        "date": review_date,
                                        "text": text})

        if created.inserted_id:
            db.user.update_one({"user_id": user_id}, {"$inc": {
                "review_count": 1}})
            my_reviews = db.review.find({"user_id": user_id})
            average = 0
            for review in my_reviews:
                average += int(review['stars'])
            average /= db.review.count_documents({"user_id": user_id})
            db.user.update_one({"user_id": user_id},
                               {"$set": {"average_stars": average}})
            print("\nReview successfully made!\n")
        else:
            print("\nAn error occurred. Please try again.\n")
    else:
        print("No business found. Try a different search!\n")


# Query 19: Update a review you made for a business
def update_user_review(db, user_id):
    review_id = input("Enter a Review ID: ")
    review = db.review.find_one({"review_id": review_id, "user_id": user_id})
    if review:
        display_review(db, review)
        updated_stars = input("Enter a new rating (1 - 5): ")
        updated_text = input("Enter your updated review: ")
        updated_date = str(date.today())
        updated = db.review.update_one({"review_id": review_id},
                                       {"$set": {"stars": updated_stars,
                                                 "date": updated_date,
                                                 "text": updated_text}})

        if updated.modified_count:
            my_reviews = db.review.find({"user_id": user_id})
            average = 0
            for r in my_reviews:
                average += int(r['stars'])
            average /= db.review.count_documents({"user_id": user_id})
            db.user.update_one({"user_id": user_id},
                               {"$set": {"average_stars": average}})
            print("\nReview successfully updated!\n")
        else:
            print("\nUpdate failed. Please try again.\n")
    else:
        print("No review found. Try a different search!\n")


# Query 20: Delete a review you made for a business
def delete_user_review(db, user_id):
    review_id = input("Enter a Review ID: ")
    review = db.review.find_one({"review_id": review_id, "user_id": user_id})
    if review:
        deleted = db.review.delete_one({"review_id": review_id})

        if deleted.deleted_count:
            db.user.update_one({"user_id": user_id},
                               {"$inc": {"review_count": -1}})

            my_reviews = db.review.find({"user_id": user_id})
            total_reviews = db.review.count_documents({"user_id": user_id})
            average = 0
            if total_reviews:
                for review in my_reviews:
                    average += int(review['stars'])
                average /= total_reviews
            db.user.update_one({"user_id": user_id},
                               {"$set": {"average_stars": average}})
            print("\nReview successfully deleted!\n")
        else:
            print("\nDelete failed. Please try again.\n")
    else:
        print("No review found. Try a different search!\n")


def get_business(db, business_id):
    return db.business.find_one({"business_id": business_id})


def display_review(db, review):
    user = db.user.find_one({"user_id": review['user_id']})
    business = get_business(db, review["business_id"])
    print(f"Review ID: {review['review_id']}\n"
          f"User: {user['name']} (ID: {user['user_id']})\n"
          f"Business: {business['name']} (ID: {business['business_id']})\n"
          f"Date: {review['date']}\n"
          f"Rating: {review['stars']}\n"
          f"Useful: {review.get('useful', 0)} votes\n"
          f"Funny: {review.get('funny', 0)} votes\n"
          f"Cool: {review.get('cool', 0)} votes\n"
          f"Review: {review['text']}\n")


def display_user(user):
    print(f"User: {user['name']} (ID: {user['user_id']})\n"
          f"User Since: {user['yelping_since']}\n"
          f"Number of Reviews: {user['review_count']}\n"
          f"Number of Useful Reviews: {user['useful']}\n"
          f"Number of Funny Reviews: {user['funny']}\n"
          f"Number of Cool Reviews: {user['cool']}\n"
          f"Number of Fans: {user['fans']}\n"
          f"Average Rating of All Reviews: {user['average_stars']}\n")


def display_business(business):
    print(f"Business: {business['name']} (ID: {business['business_id']})\n"
          f"Address: {business.get('address', 'N/A')}, {business['city']}, "
          f"{business['state']}, {business['postal_code']}\n"
          f"Categories: {business['categories']}\n"
          f"Average Rating: {business['stars']}\n"
          f"Number of Reviews: {business['review_count']}\n")


def generate_id():
    return ''.join(random.choice(string.ascii_letters) for i in range(22))


def main():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.yelp  # yelp = name of our database
    print("Loading database and indexes...\n")

    db.business.create_index([("business_id", 1)], unique=True)
    db.business.create_index([("state", 1), ("city", 1)])
    db.business.create_index([("zipcode", 1)])
    db.business.create_index([("review_count", 1)])

    db.user.create_index([("user_id", 1)], unique=True)
    db.user.create_index([("name", 1)])
    db.user.create_index([("review_count", 1)])

    db.review.create_index([("review_id", 1)], unique=True)
    db.review.create_index([("business_id", 1)])
    db.review.create_index([("user_id", 1)])

    main_menu(db)
    print("Thanks for using the Business Reviews System! Goodbye!\n")


if __name__ == '__main__':
    main()
