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


def main_menu(db):
    choice = True
    while choice:
        print(f"{25 * '='} MAIN MENU {25 * '='}")
        print("Welcome to the Business Reviews System!\n"
              "To begin, please login or create an account.\n"
              "[1] = Login\n"
              "[2] = Register\n"
              "[0] = Exit\n")
        choice = int(input("Enter your choice: "))
        print("\n")
        if choice == 1:
            login(db)
        elif choice == 2:
            register(db)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


def login(db):
    print(f"{27 * '='} LOGIN {27 * '='}")
    user = None
    while not user:
        name = input("Enter username: ")
        password = input("Enter password: ")
        user = db.user.find_one({"$and": [{"password": {"$exists": True}},
                                          {"password": password}],
                                 "name": name})
    print(f"Hi {user['name']}, you are now logged in!")
    print("\n\n")
    initial_choices(db, user["user_id"])


# Query 1: Create an account
def register(db):
    print(f"{25 * '='} REGISTER {25 * '='}")
    user_id = generate_id()
    name = input("Enter a username: ")
    password = input("Enter a password: ")
    db.user.insert_one({"user_id": user_id, "name": name,
                        "password": password})
    print("Account successfully created! Please login...")
    print(61 * '=')
    login(db)


def initial_choices(db, user_id):
    choice = True
    while choice:
        print(f"{20 * '='} BUSINESS REVIEWS SYSTEM {20 * '='}")
        print("[1] = Search\n"
              "[2] = View\n"
              "[3] = My Reviews\n"
              "[0] = Exit")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            search_prompt(db, user_id)
        elif choice == 2:
            view_prompt(db, user_id)
        elif choice == 3:
            user_reviews_prompt(db, user_id)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


def search_prompt(db, user_id):
    print(f"{25 * '='} SEARCH {25 * '='}")
    print("[1] = Search Businesses\n"
          "[2] = Search Users\n"
          "[0] = Return")
    print(61 * '=')
    choice = True
    while choice:
        choice = int(input("Enter your choice: "))
        if choice == 1:
            search_business_prompt(db, user_id)
        elif choice == 2:
            search_users(db)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


def search_business_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{25 * '='} SEARCH BUSINESSES {25 * '='}")
        print("[1] = Search By City & State\n"
              "[2] = Search By Zipcode\n"
              "[0] = Return")
        print("\n\n")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            search_business_by_city_state(db, user_id)
        elif choice == 2:
            search_business_by_zipcode(db, user_id)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 2: Search for business by city
def search_business_by_city_state(db, user_id):
    city = input("Enter a city: ")
    state = input("Enter a state: ")
    db.business.find({"city":city,"state":state})
    search_business_by_attributes_prompt(db, user_id, city=city, state=state)


# Query 3: Search for business by zip code
def search_business_by_zipcode(db, user_id):
    zipcode = input("Enter a zipcode: ")
    db.business.find({"zipcode":zipcode})
    search_business_by_attributes_prompt(db, user_id, zipcode=zipcode)


def search_business_by_attributes_prompt(db, user_id, **kwargs):
    choice = True
    while choice:
        print(f"{25 * '='} SEARCH BUSINESSES {25 * '='}")
        print("[1] = Search By Name\n"
              "[2] = Search By Category\n"
              "[3] = Search By Rating\n"
              "[0] = New Search")
        print("\n\n")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            search_business_by_name(db, user_id, **kwargs)
        elif choice == 2:
            search_business_by_category(db, user_id, **kwargs)
        elif choice == 3:
            search_business_by_rating(db, user_id, **kwargs)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 4: Search for business by name
def search_business_by_name(db, user_id, **kwargs):
    name = input("Enter a name: ")
    if "city" in kwargs.keys() and "state" in kwargs.keys():
        # Make query filters that involve city and state fields
        db.business.find({"name":name,"city":kwargs.get("city"),"state";kwargs.get("state")})
        pass
    else:
        # Make query filters that involve zipcode field
        db.business.find({"name":name,kwargs.get("zipcode")})
        pass
    view_or_create_reviews_prompt(db, user_id)


# Query 5: Search for business by category
def search_business_by_category(db, user_id, **kwargs):
    category = input("Enter a category: ")
    if "city" in kwargs.keys() and "state" in kwargs.keys():
        # Make query filters that involve city and state fields
         db.business.find({"category":category,"city":kwargs.get("city"),"state":kwargs.get("state")})
        pass
    else:
        # Make query filters that involve zipcode field
        db.business.find({"category":category,"zipcode":kwargs.get("zipcode")})
        pass
    view_or_create_reviews_prompt(db, user_id)


# Query 6: Search for business by rating
def search_business_by_rating(db, user_id, **kwargs):
    rating = int(input("Enter a rating: "))
    if "city" in kwargs.keys() and "state" in kwargs.keys():
        # Make query filters that involve city and state fields
        db.business.find({"rating":rating,"city":kwargs.get("city"),"state":kwargs.get("state")})
        pass
    else:
        # Make query filters that involve zipcode field
        db.business.find({"rating":rating,"zipcode":kwargs.get("zipcode")})
        pass
    view_or_create_reviews_prompt(db, user_id)


# Query 7: Search for users
def search_users(db):
    name = input("Enter a name: ")
    db.users.find({"name":name})


def view_or_create_reviews_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{25 * '='} VIEW & CREATE REVIEWS {25 * '='}")
        print("[1] = View A Business's Reviews\n"
              "[2] = Give A Review\n"
              "[0] = New Search")
        print("\n\n")
        choice = input("Enter your choice: ")
        if choice == 1:
            view_business_reviews_prompt(db)
        elif choice == 2:
            create_user_review(db, user_id)
        else:
            print("Invalid input, please try again\n")


def view_business_reviews_prompt(db):
    business_id = input("Enter a business id: ")
    choice = True
    while choice:
        print(f"{25 * '='} VIEW REVIEWS {25 * '='}")
        print("[1] = View All Reviews\n"
              "[2] = View Most Useful Review\n"
              "[3] = View Funniest Review\n"
              "[4] = View Coolest Review\n"
              "[0] = New Search")
        print("\n\n")
        choice = input("Enter your choice: ")
        if choice == 1:
            view_all_business_reviews(db, business_id)
        elif choice == 2:
            view_most_useful_business_review(db, business_id)
        elif choice == 3:
            view_funniest_business_review(db, business_id)
        elif choice == 4:
            view_coolest_business_review(db, business_id)
        else:
            print("Invalid input, please try again\n")


# Query 12: View a business's reviews
def view_all_business_reviews(db, business_id):
    pass


# Query 13: View most useful review of a business
def view_most_useful_business_review(db, business_id):
    pass


# Query 14: View funniest review of a business
def view_funniest_business_review(db, business_id):
    review = db.review.find({"business_id": business_id}).sort("funny",
                                                               -1).limit(1)
    if review:
        reviewer = get_user(db, review["user_id"])
        business = get_business(db, business_id)
        print(f"review_id: {review['review_id']}"
              f"Business: {business['name']} ({business_id})"
              f"Reviewer: {reviewer['name']} ({reviewer['user_id']})"
              f"Useful: {review['useful']} votes"
              f"Date: {review['date']}"
              f"Review: {review['text']}")
    else:
        print("No reviews found. Try a different search!")


# Query 15: View coolest review of a business
def view_coolest_business_review(db, business_id):
    review = db.review.find({"business_id": business_id}).sort("cool",
                                                               -1).limit(1)
    if review:
        reviewer = get_user(db, review["user_id"])
        business = get_business(db, business_id)
        print(f"review_id: {review['review_id']}"
              f"Business: {business['name']} ({business_id})"
              f"Reviewer: {reviewer['name']} ({reviewer['user_id']})"
              f"Cool: {review['cool']} votes"
              f"Date: {review['date']}"
              f"Review: {review['text']}")
    else:
        print("No reviews found. Try a different search!")


def view_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{25 * '='} VIEW {25 * '='}")
        print("[1] = View My Profile\n"
              "[2] = View Top 10 Businesses\n"
              "[3] = View Most Reviewed Businesses\n"
              "[4] = View Most Prolific Reviewer\n"
              "[5] = View Harshest Critic\n"
              "[0] = Return")
        print("\n\n")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            view_user_profile(db, user_id)
        elif choice == 2:
            view_top_rated_businesses(db)
        elif choice == 3:
            view_most_rated_businesses(db)
        elif choice == 4:
            view_user_most_reviews(db)
        elif choice == 5:
            view_user_lowest_average_rating(db)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 11: View your account profile
def view_user_profile(db, user_id):
    pass


# Query 8: View top 10 businesses
def view_top_rated_businesses(db):
    pass


# Query 9: View most reviewed businesses
def view_most_rated_businesses(db):
    pass


# Query 16: View user with the most reviews
def view_user_most_reviews(db):
    user = db.user.find().sort("review_count", -1).limit(1)
    print(f"User: {user['name']} ({user['user_id']})"
          f"User Since: {user['yelping_since']}"
          f"Number of Reviews: {user['review_count']}")


# Query 17: View user that is the harshest critic
def view_user_lowest_average_rating(db):
    user = db.user.find({"average_stars": {"$exists": True},
                         "review_count": {"$gt": 100}}).sort(
        "average_stars", 1).limit(1)
    print(f"User: {user['name']} ({user['user_id']})"
          f"User Since: {user['yelping_since']}"
          f"Average Rating For Reviews: {user['average_stars']}"
          f"Number of Reviews: {user['review_count']}")


def user_reviews_prompt(db, user_id):
    choice = True
    while choice:
        print(f"{25 * '='} MY REVIEWS {25 * '='}")
        print("[1] = View My Reviews\n"
              "[2] = Make A Review\n"
              "[3] = Update A Review\n"
              "[4] = Delete A Review\n"
              "[0] = Return")
        choice = int(input("Enter your choice: "))
        print("\n\n")
        if choice == 1:
            view_user_reviews(db, user_id)
        elif choice == 2:
            create_user_review(db, user_id)
        elif choice == 3:
            update_user_review(db)
        elif choice == 4:
            delete_user_review(db)
        elif choice == 0:
            choice = False
        else:
            print("Invalid input, please try again\n")


# Query 10: View all reviews made by your account
def view_user_reviews(db, user_id):
    pass


# Query 18: Create a review for a business
def create_user_review(db, user_id):
    business_id = input("Enter a business id: ")
    stars = int(input("Rate this business (1 - 5): "))
    text = input("Write your review: ")
    review_id = generate_id()
    review_date = str(date.today())
    object_id = db.review.insert_one({"review_id": review_id,
                                      "user_id": user_id,
                                      "business_id": business_id,
                                      "stars": stars,
                                      "date": review_date,
                                      "text": text})
    if object_id:
        print("Review successfully made!")
    else:
        print("An error occurred. Please try again.")


# Query 19: Update a review you made for a business
def update_user_review(db):
    review_id = input("Enter a review id: ")
    review = get_review(db, review_id)
    if review:
        display_review(db, review_id)
        print(61 * '=')
        updated_stars = input("Enter a new rating (1 - 5): ")
        updated_text = input("Enter your updated review: ")
        updated_date = str(date.today())
        updated = db.review.update_one({"review_id": review_id},
                                       {"$set": {"stars": updated_stars,
                                                 "date": updated_date,
                                                 "text": updated_text}})
        if updated:
            print("Review successfully updated!")
        else:
            print("Update failed. Please try again.")
    else:
        print("No review found. Please try again.")


# Query 20: Delete a review you made for a business
def delete_user_review(db):
    review_id = input("Enter a review id: ")
    deleted = db.review.delete_one({"review_id": review_id})
    if deleted:
        print("Review deleted!")
    else:
        print("No review found. Please try again.")


def get_user(db, user_id):
    return db.user.find_one({"user_id": user_id})


def get_business(db, business_id):
    return db.business.find_one({"business_id": business_id})


def get_review(db, review_id):
    return db.review.find_one({"review_id": review_id})


def display_review(db, review_id):
    review = get_review(db, review_id)
    user = get_user(db, review["user_id"])
    business = get_business(db, review["business_id"])
    print(f"Review ID: {review['review_name']}"
          f"User: {user['name']} ({user['user_id']})"
          f"Business: {business['name']} ({business['business_id']})"
          f"Date: {review['date']}"
          f"Rating: {review['stars']}"
          f"Review: {review['text']}")


def generate_id():
    return ''.join(random.choice(string.ascii_letters) for i in range(22))


def main():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.yelp  # yelp = name of our database
    print("Loading database and indexes...\n")
    db.business.create_index([("business_id", 1)], unique=True)
    db.user.create_index([("user_id", 1)], unique=True)
    db.review.create_index([("review_id", 1)], unique=True)
    main_menu(db)
    print("Thanks for using the Business Reviews System! Goodbye!\n")


if __name__ == '__main__':
    main()
