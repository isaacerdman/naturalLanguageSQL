import argparse
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

    ask_chatgpt("Why is the sky blue?", openAiSecretKey)

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
        ("Potato taco", "FALSE"), # 5 Taco Bell
        ("Burger", "FALSE"), # 6 Carls Jr
        ("Impossible Burger", "FALSE"), # 7 Curls Jr
        ("Tirimisu", "TRUE"), # 8 Buca De Peppo
        ("Grilled Chicken Burrito", "TRUE"), # 9 Del Taco
        ("Machine Gun Sandwich", "FALSE"),  # 10 Bruges
        ("Soup", "True"),  # 11 Olive Garden
    ]

    defaultMenuTable = [
        ("1", "2"), # Olive garden has spagetti
        ("1", "11"), # Olive garden has soup
        ("2", "1"), # Papa johns has olive pizza
        ("3", "3"),
        ("3", "5"),
        ("4", "4"),
        ("4", "10"),
        ("5", "3"),
        ("5", "9"),
        ("6", "1"),
        ("6", "8"),
        ("7", "6"),
        ("7", "7"),
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
        cursor.execute("SELECT * FROM restaurants")
        result = cursor.fetchall()
        conn.commit()

    for row in result:
        print(row)


if __name__ == '__main__':
    main()