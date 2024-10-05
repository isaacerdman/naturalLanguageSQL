import argparse
import re

import psycopg2
from chatGPT import ask_chatgpt


def main():
    parser = argparse.ArgumentParser(description='Handle connection string input')

    # Argument gets passed in as: """ -c="Your URL HERE" """
    parser.add_argument('-c', type=str, required=True,
                        help='connection string for database')
    parser.add_argument('-k', type=str, required=True,
                        help='key for open ai')
    
    args = parser.parse_args()
    connectionString = args.c
    openAiSecretKey = args.k

    dropMenuTable = """
    DROP TABLE IF EXISTS Menu;
    """

    dropRestaurantsTable = """
    DROP TABLE IF EXISTS Restaurants;
    """

    dropFoodItemTable = """
    DROP TABLE IF EXISTS FoodItem;
    """

    createFoodItemTable = """
    CREATE TABLE IF NOT EXISTS FoodItem (
        foodId SERIAL PRIMARY KEY,
        name VARCHAR(45) NOT NULL UNIQUE,
        vegetarian BOOLEAN DEFAULT FALSE
    );
    """

    createRestaurantTable = """
    CREATE TABLE IF NOT EXISTS Restaurants (
        restaurantId SERIAL PRIMARY KEY,
        name VARCHAR(45) NOT NULL,
        cuisine VARCHAR(45)
    );
    """

    createMenuTable = """
    CREATE TABLE IF NOT EXISTS Menu (
        restaurantId INTEGER NOT NULL,
        foodId INTEGER NOT NULL,
        PRIMARY KEY (restaurantId, foodId),
        FOREIGN KEY (foodId) REFERENCES FoodItem (foodId) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (restaurantId) REFERENCES Restaurants (restaurantId) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """

    insertRestaurants = """
      INSERT INTO Restaurants (name, cuisine)
      VALUES (%s, %s)
    """

    insertFoodItems = """
      INSERT INTO FoodItem (name, vegetarian)
      VALUES (%s, %s)
    """

    insertMenus = """
      INSERT INTO Menu (restaurantId, foodId)
      VALUES (%s, %s)
    """

    defaultRestaurants = [
        ("Olive Garden", "Italian"),
        ("Papa Johns", "American"),
        ("Taco Bell", "Mexican"),
        ("Bruges", "Belgian"),
        ("Del Taco", "Mexican"),
        ("Buca De Beppo", "Italian"),
        ("Carls Jr", "Armerican"),
    ]

    defaultFoodItems = [
        ("Olive Pizza", "TRUE"), # 1 papa johns, Buca De Peppo
        ("Spagetti", "FALSE"), # 2 Buca De Peppo
        ("Taco", "FALSE"), # 3 Taco Bell, Del Taco
        ("Chicken And Waffles", "FALSE"), # 4 Bruges
        ("Potato taco", "TRUE"), # 5 Taco Bell
        ("Burger", "FALSE"), # 6 Carls Jr
        ("Impossible Burger", "TRUE"), # 7 Carls Jr
        ("Tirimisu", "TRUE"), # 8 Buca De Peppo
        ("Grilled Chicken Burrito", "FALSE"), # 9 Del Taco
        ("Machine Gun Sandwich", "FALSE"),  # 10 Bruges
        ("Soup", "True"),  # 11 Olive Garden
    ]

    defaultMenuTable = [
        ("1", "2"), # Olive garden has spagetti
        ("1", "11"), # Olive garden has soup
        ("2", "1"), # Papa johns has olive pizza
        ("3", "3"), # Taco bell has taco
        ("3", "5"), # Taco bell has potato taco
        ("4", "4"), # Bruges Chicken and waffles
        ("4", "10"), # Bruges Machine Gun Sandwich
        ("5", "3"), # Del Taco has taco
        ("5", "9"), # Del Taco has Grilled Chicken
        ("6", "1"), # Buca has Olive Pizza
        ("6", "8"), # Buca has Tirimisu
        ("7", "6"), # Carls Jr has Burger
        ("7", "7"), # Carls Jr has Impossible Burger
    ]


    with psycopg2.connect(connectionString) as conn:
        cursor = conn.cursor()
        # Drop things so we get a fresh start
        cursor.execute(dropMenuTable)
        cursor.execute(dropRestaurantsTable)
        cursor.execute(dropFoodItemTable)
        # Now make them again! Yay!
        cursor.execute(createFoodItemTable)
        cursor.execute(createRestaurantTable)
        cursor.execute(createMenuTable)
        cursor.executemany(insertRestaurants, defaultRestaurants)
        cursor.executemany(insertFoodItems, defaultFoodItems)
        cursor.executemany(insertMenus, defaultMenuTable)
        conn.commit()

        cursor.execute("SELECT * FROM Restaurants")
        resultRestaurants = cursor.fetchall()

        cursor.execute("SELECT * FROM FoodItem")
        resultFoodItems = cursor.fetchall()

        cursor.execute("SELECT * FROM Menu")
        resultMenuItems = cursor.fetchall()

    for row in resultRestaurants:
        print(row)

    print("\n")

    for row in resultFoodItems:
        print(row)

    print("\n")

    for row in resultMenuItems:
        print(row)

    # prompt for a question
    question = input("What is your question about the data base?")
    schemaString = createFoodItemTable + "\n" + createMenuTable + "\n" + createRestaurantTable


    # ask CHAT GPT
    generatedSqlStatement = ask_chatgpt("Given the following schema information, return only a valid postgreSQL statement to query the database: " + schemaString + "\nHere is the question: " + question, openAiSecretKey)
    generatedSqlStatementRevised = ask_chatgpt("I have this SQL statement, can I have it corrected to valid PostgreSQL syntax? Return only a valid postgreSQL statement to query the database: " + generatedSqlStatement, openAiSecretKey)
    # Run the SQL query form Chat
    print(generatedSqlStatementRevised)
    if generatedSqlStatementRevised.__contains__("```"):
        generatedSqlStatementRevised = re.search(r'```sql\s*(.*?)\s*```', generatedSqlStatementRevised, re.DOTALL).group(1)

    with psycopg2.connect(connectionString) as conn:
        cursor = conn.cursor()
        cursor.execute(generatedSqlStatementRevised)
        queryResult = cursor.fetchall()

    # capture results
    response = ""
    for row in queryResult:
        response = response + "\n" + str(row)

    # ask chat gpt to interpret results
    friendlyResponse = ask_chatgpt("From this question: " + question + "\nInterpret the response in plain english (If the response is nothing, tell me that): " + response, openAiSecretKey)

    # Return to user
    print(friendlyResponse)

    print("\n")


if __name__ == '__main__':
    main()
